from .db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey
from sqlalchemy import orm
from datetime import datetime


class Project(SqlAlchemyBase):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.now)

    price = Column(Integer, default=0)

    files = Column(LargeBinary, nullable=False)
    imgs = Column(LargeBinary, nullable=False)

    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_by_user = orm.relationship("User", foreign_keys=[created_by_user_id])
