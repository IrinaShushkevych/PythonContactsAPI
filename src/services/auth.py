import redis
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import pickle

from src.repository import auth as repository_auth
from src.database.connect import get_db
from src.conf.config import settings


class Auth:
    algorithm = settings.algorithm
    secret_key = settings.secret_key
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
    auth_redis = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)

    def create_password_hash(self, password: str):
        """
        The create_password_hash function takes a password as an argument and returns the hashed version of that
        password. The hash is generated using the pwd_context object's hash method, which uses PBKDF2 to generate a
        secure hash.

        :param self: Represent the instance of the class
        :param password: str: Specify the password that is being hashed
        :return: A hash of the password that is passed to it
        """
        return self.pwd_context.hash(password)

    def verify_password_hash(self, password: str, hashed_password: str):
        """
        The verify_password_hash function takes a plain-text password and a hashed password,
        and returns True if the passwords match, False otherwise. This function is used to verify
        that the user's inputted password matches their stored hash.

        :param self: Make the function a method of the user class
        :param password: str: Pass in the password that the user entered
        :param hashed_password: str: Pass in the hashed password that is stored in the database
        :return: A boolean
        """
        return self.pwd_context.verify(password, hashed_password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.

        :param self: Refer to the current object
        :param data: dict: Pass the data that will be encoded in the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A token that is encoded with the secret key
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=10)
        to_encode.update({'exp': expire, 'iat': datetime.utcnow(), 'scope': 'access_token'})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token. Args: data (dict): A dictionary containing the
        user's id and username. expires_delta (Optional[float]): The time in seconds until the token expires.
        Defaults to None, which is 7 days from now.

        :param self: Represent the instance of the class
        :param data: dict: Pass the user's data to be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A refresh token that is encoded with the user's id and email
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'exp': expire, 'iat': datetime.utcnow(), 'scope': 'refresh_token'})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def decode_refresh_token(self, token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It will return the user id if it's a valid refresh token, otherwise it will raise an exception.

        :param self: Represent the instance of the class
        :param token: str: Pass the token that we want to decode
        :return: The user_id of the user who has requested a new access token
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload['scope'] == 'refresh_token':
                return payload['sub']
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credential')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            object if it exists, otherwise it raises an exception.

        :param self: Access the class attributes
        :param token: str: Get the token from the request header
        :param db: Session: Get the database session
        :return: A user object
        """
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
        """
        The create_email_token function takes a dictionary of data and returns a token.
        The token is created using the secret_key and algorithm defined in the class.
        The data dictionary must contain an email key, which will be used to create the token.

        :param self: Make the function a method of the class
        :param data: dict: Pass in the data that will be encoded
        :return: A token that is encoded using jwt
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with
        that token. The function uses the jwt library to decode the token, which is then used to return the email
        address.

        :param self: Represent the instance of a class
        :param token: str: Pass in the token that is sent to the user's email
        :return: The email address of the user who is trying to verify their account
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email = payload['sub']
            return email
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Invalid token for email verification')


auth_service: Auth = Auth()
