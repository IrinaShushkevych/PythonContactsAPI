from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_username),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)


async def send_mail_verify(email: EmailStr, username: str, host: str):
    try:
        token = await auth_service.create_email_token({'sub': email})
        message = MessageSchema(
            subject='Confirm your email',
            recipients=[email],
            template_body={'host': host, 'username': username, 'token': token},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name='email_verification.html')
    except ConnectionErrors as e:
        print(e)


async def send_mail_password(email: EmailStr, username: str, host: str):
    try:
        token = await auth_service.create_email_token({'sub': email})
        message = MessageSchema(
            subject='Reset password',
            recipients=[email],
            template_body={'host': host, 'username': username, 'token': token},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name='email_password.html')
    except ConnectionErrors as e:
        print(e)
