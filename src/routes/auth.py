from fastapi import APIRouter, HTTPException, status, Security, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from src import get_db, UserModel, UserResponse, TokenModel, repository_auth, User
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    user = await repository_auth.get_user_by_email(body.email, db)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = auth_service.create_password_hash(body.password)
    user = await repository_auth.create_user(body, db)
    return {'user': user, 'detail': 'User successfully created'}


@router.post('/login', response_model=TokenModel, status_code=status.HTTP_201_CREATED)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_auth.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')

    if not auth_service.verify_password_hash(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')

    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await repository_auth.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
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


@router.get('/logout', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(auth_service.get_current_user),
                 db: Session = Depends(get_db)):
    if current_user.refresh_token == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authorized')
    await repository_auth.update_token(current_user, None, db)

    return {'user': current_user, 'detail': 'User successfully logout'}







#
# @router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def signup(body: UserModel, db: Session = Depends(get_db)):
#     exist_user = await repository_auth.get_user_by_email(body.email, db)
#     if exist_user:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
#     body.password = auth_service.get_password_hash(body.password)
#     new_user = await repository_auth.create_user(body, db)
#     return {"user": new_user, "detail": "User successfully created"}
#
#
# @router.post("/login", response_model=TokenModel)
# async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = await repository_auth.get_user_by_email(body.username, db)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
#     if not auth_service.verify_password(body.password, user.password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
#     # Generate JWT
#     access_token = await auth_service.create_access_token(data={"sub": user.email})
#     refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
#     await repository_auth.update_token(user, refresh_token, db)
#     return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
#
#
# @router.get('/refresh_token', response_model=TokenModel)
# async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
#     token = credentials.credentials
#     email = await auth_service.decode_refresh_token(token)
#     user = await repository_auth.get_user_by_email(email, db)
#     if user.refresh_token != token:
#         await repository_auth.update_token(user, None, db)
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
#
#     access_token = await auth_service.create_access_token(data={"sub": email})
#     refresh_token = await auth_service.create_refresh_token(data={"sub": email})
#     await repository_auth.update_token(user, refresh_token, db)
#     return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
#
#
