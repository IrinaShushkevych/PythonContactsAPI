from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src import User, UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Retrieves user by email
    :param email: User email.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: User.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user
    :param body: The data for the user to create.
    :param db: The database session.
    :type db: Session
    :return: User.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict())
    new_user.avatar = avatar
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update token for user.
    :param user: User whose token needs to be changed.
    :type user: User
    :param token: A new token.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_user(email: str, db: Session) -> None:
    """
    Set flag "confirmed" for user.
    :param email:  User email.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, avatar_url: str, db: Session) -> User:
    """
    Update user avatar.
    :param email: User email.
    :type email: str
    :param avatar_url: Avatar url.
    :type avatar_url: str
    :param db: The database session.
    :type db: Session
    :return: User.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = avatar_url
    db.commit()
    return user


async def update_password(email: str, password: str, db: Session) -> User:
    """
    Update user password.
    :param email: User email.
    :type email: str
    :param password: User password.
    :type password: str
    :param db: The database session.
    :type db: Session
    :return: User.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.password = password
    db.commit()
    return user
