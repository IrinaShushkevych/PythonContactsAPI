import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, status, Depends, File, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src import get_db, repository_auth, User, UserDB, ResetPassword, RequestEmail, UserResponse
from src.services.auth import auth_service
from src.conf.config import settings
from src.services.email import send_mail_password

router = APIRouter(prefix='/users', tags=["users"])
security = HTTPBearer()


@router.get('/me/', response_model=UserDB, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def get_user_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserDB, description='No more than 5 requests per minute',
              dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_200_OK)
async def update_avatar(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
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


@router.post('/forgot_password', description='No more than 3 requests per minute',
             dependencies=[Depends(RateLimiter(times=3, seconds=60))], status_code=status.HTTP_200_OK)
async def forgot_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                          db: Session = Depends(get_db)):
    user = await repository_auth.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account does not exists')

    background_tasks.add_task(send_mail_password, user.email, user.username, request.base_url)
    return {'message': 'Email was send'}


@router.post('/reset_password/{token}', response_model=UserResponse, description='No more than 3 requests per minute',
             dependencies=[Depends(RateLimiter(times=3, seconds=60))], status_code=status.HTTP_200_OK)
async def reset_password(token: str, body: ResetPassword, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_auth.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')

    if body.password == body.password_confirm:
        password = auth_service.create_password_hash(body.password)
        user = await repository_auth.update_password(email, password, db)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password doesn't confirmed")

    return {'user': user, 'detail': 'Password was changed'}
