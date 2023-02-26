from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ContactsModel(BaseModel):
    firstname: str = Field(min_length=2, max_length=150)
    lastname: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=4, max_length=20)
    born_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class ContactsResponse(ContactsModel):
    id: int

    class Config:
        orm_mode = True


class ContactsBirthday(BaseModel):
    born_date: date


class ContactsNotes(BaseModel):
    notes: str = Field(max_length=500)


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserDB(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDB
    detail: str = 'User successfully created'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    password: str
    password_confirm: str
