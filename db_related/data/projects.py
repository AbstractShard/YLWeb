from .db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime


class Project(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.now)

    price = Column(Integer, default=0)

    # Store file paths instead of binary data
    files = Column(String, nullable=False)  # Path to project ZIP
    imgs = Column(String, nullable=False)   # Path to images ZIP

    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_by_user = orm.relationship("User", foreign_keys=[created_by_user_id], back_populates="created_projects")

    purchased_by_users = orm.relationship(
        "User", 
        secondary="user_project_association",
        back_populates="purchased_projects",
        uselist=True
    )
