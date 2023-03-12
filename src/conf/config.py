from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_url: str
    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    algorithm: str
    secret_key: str
    redis_host: str
    redis_port: int
    redis_db: int
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    main_host: str
    main_port: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        allow_mutation = True


settings = Settings()
