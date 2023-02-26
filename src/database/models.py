from sqlalchemy import Column, Integer, String, Date, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime


Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(150), nullable=False)
    lastname = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    born_date = Column(Date, nullable=True)
    notes = Column(String(500), nullable=True)
    user_id = Column('user_id', ForeignKey('users.id', ondelete="CASCADE"))
    user = relationship("User", backref="contacts")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)

    def __str__(self):
        return f'{self.id}({type(self.id)}), {self.username}({type(self.username)}), {self.email}({type(self.email)}),' \
               f' {self.password}({type(self.password)}), {self.created_at}({type(self.created_at)}), {self.refresh_token},' \
               f'({type(self.refresh_token)}), {self.avatar}({type(self.avatar)})'