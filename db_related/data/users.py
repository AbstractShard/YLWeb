from sqlalchemy import Column, Integer, String, LargeBinary
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Информация о пользователе
    name = Column(String, nullable=False)
    about = Column(String, nullable=True)
    img = Column(LargeBinary, nullable=False)
    currency = Column(Integer, nullable=False, default=0)

    # Информация нужная для логина
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def set_password(self, password: str):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)
