from fastapi import APIRouter, HTTPException, status, Security, Depends, BackgroundTasks, Request, File, UploadFile
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
import cloudinary
import cloudinary.uploader

from src import get_db, UserModel, UserResponse, TokenModel, repository_auth, User, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_mail_verify
from src.conf.config import settings

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, description='No more than 5 requests per minute',
             dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes an email, username and password as input.
        The password is hashed before being stored in the database.

    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A dictionary with the user and a detail message
    """
    user = await repository_auth.get_user_by_email(body.email, db)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = auth_service.create_password_hash(body.password)
    user = await repository_auth.create_user(body, db)

    background_tasks.add_task(send_mail_verify, user.email, user.username, request.base_url)
    return {'user': user, 'detail': 'User successfully created'}


@router.post('/login', response_model=TokenModel, description='No more than 5 requests per minute',
             dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_201_CREATED)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes the email and password of the user as input,
        checks if they are valid, and returns an access token.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get a database session
    :return: A token
    """
    user = await repository_auth.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')

    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')

    if not auth_service.verify_password_hash(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')

    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await repository_auth.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/refresh_token', response_model=TokenModel, description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_200_OK)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns a new access_token,
        refresh_token, and the type of token (bearer).

    :param credentials: HTTPAuthorizationCredentials: Get the token from the authorization header
    :param db: Session: Get a database session
    :return: A dict with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_auth.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_auth.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    access_token = await auth_service.create_access_token(data={'sub': email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': email})
    await repository_auth.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/logout', response_model=UserResponse, description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(auth_service.get_current_user),
                 db: Session = Depends(get_db)):
    """
    The logout function is used to logout a user.
        It takes the current_user as an argument and returns a dict with the user and detail.

    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the function
    :return: A dict with the user and a message
    """
    if current_user.refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authorized')
    await repository_auth.update_token(current_user, None, db)

    return {'user': current_user, 'detail': 'User successfully logout'}


@router.get('/confirmed_email/{token}', description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_200_OK)
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        The function then checks if there is a user with that email in our database, and if not, returns an error message.
        If there is a user with that email in our database, we check whether their account has already been confirmed or not.
            If it has been confirmed already, we return another error message saying so; otherwise we confirm their account.

    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A message to the user.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_auth.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    await repository_auth.confirmed_user(email, db)
    return {'message': 'Email confirmed'}


@router.post('/request_email', description='No more than 5 requests per minute',
             dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_200_OK)
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send a verification email to the user.
    It takes in an email address and sends a confirmation link to that address.
    The function also checks if the user has already confirmed their account, and returns an error message if they have.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :return: A message to the user
    """
    user = await repository_auth.get_user_by_email(body.email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')

    if user.confirmed:
        return {'message': 'Your email is already confirmed'}

    background_tasks.add_task(send_mail_verify, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.patch('/avatar', description='No more than 5 requests per minute',
              dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_200_OK)
async def update_avatar(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    """
    The update_avatar function is used to update the avatar of a user.
    It takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
    The current_user and db objects are also passed into this function, as they are required for updating
    the avatar URL in the database.

    :param file: UploadFile: Get the file from the request
    :param current_user: User: Get the current user information
    :param db: Session: Pass the database session to the repository layer
    :return: The updated user object
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    cloudinary.uploader.upload(file.file, public_id=f'PythonContactsApp/{current_user.username}',
                               overwrite=True)
    avatar_url = cloudinary.CloudinaryImage(f'PythonContactsApp/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill')
    user = await repository_auth.update_avatar(current_user.email, avatar_url, db)
    return user
