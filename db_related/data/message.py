from sqlalchemy import Column, Integer, String, LargeBinary, Boolean, Time, DATETIME
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, UserMixin):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(Integer, nullable=False)


    # Информация о уведомлении
    data = Column(String, nullable=False)
    name = Column(String, nullable=False)
    about = Column(String, nullable=True)
    readability = Column(Boolean, nullable=False)

    # Информация нужная для транзакций
    sender = Column(String, nullable=True)
    recipient = Column(String, nullable=True)
    suma = Column(String, nullable=True)

