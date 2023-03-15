from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_url: str = "postgresql+psycopg2://"
    mail_username: str = 'IraOlijnyk@meta.ua'
    mail_password: str = 'Klop0104$$'
    mail_port: int = 465
    mail_server: str = 'smtp.meta.ua'
    mail_from_name: str = 'Irina'
    algorithm: str = 'HS256'
    secret_key: str = 'qwertyuiopazsx'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    redis_db: int = 0
    cloudinary_name: str = 'drilpksk7'
    cloudinary_api_key: str = '326193329941471'
    cloudinary_api_secret: str = '1YqMfm4NEIJApzklq_lEaolH7-I'
    main_host: str = '127.0.0.1'
    main_port: int = 8000

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        allow_mutation = True


settings = Settings()
