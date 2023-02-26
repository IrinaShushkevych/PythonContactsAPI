import redis
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import pickle


from src.repository import  auth as repository_auth
from src.database.connect import get_db
from src.conf.config import settings


class Auth:
    algorithm = settings.algorithm
    secret_key = settings.secret_key
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
    auth_redis = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)

    def create_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password_hash(self, password: str, hashed_password: str):
        return self.pwd_context.verify(password, hashed_password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=10)
        to_encode.update({'exp': expire, 'iat': datetime.utcnow(), 'scope': 'access_token'})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'exp': expire, 'iat': datetime.utcnow(), 'scope': 'refresh_token'})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def decode_refresh_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload['scope'] == 'refresh_token':
                return payload['sub']
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credential')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credential',
            headers={'WWW-Authenticate': 'Bearer'}
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.auth_redis.get(f'user:{email}')
        if user is None:
            user = await repository_auth.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.auth_redis.set(f'user:{email}', pickle.dumps(user))
            self.auth_redis.expire(f'user:{email}', 1000)
        else:
            user = pickle.loads(user)
        return user

    async def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return token

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email = payload['sub']
            return email
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Invalid token for email verification')


auth_service: Auth = Auth()
