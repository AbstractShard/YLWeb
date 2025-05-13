from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Информация о пользователе
    name = Column(String, nullable=False)
    about = Column(String, nullable=True)
    img = Column(LargeBinary, nullable=False)
    balance = Column(Integer, nullable=False, default=0)

    # Информация нужная для логина
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Для проектов
    created_projects = orm.relationship("Project", back_populates="created_by_user", foreign_keys="Project.created_by_user_id", uselist=True)

    #purchased_projects_ids = Column(Integer, ForeignKey("projects.id"))
    purchased_projects = orm.relationship(
        "Project", 
        secondary="user_project_association",
        back_populates="purchased_by_users",
        uselist=True
    )
    #purchased_projects = orm.relationship("Project", foreign_keys=[purchased_projects_ids], uselist=True)

    def set_password(self, password: str):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    def set_verify_code(self, code: str):
        self.verify_code = generate_password_hash(code)

    def check_verify_code(self, code: str) -> bool:
        return check_password_hash(self.verify_code, code)

    def set_default_img(self):
        with open("static/img/profile.png", mode="rb") as def_img:
            self.img = def_img.read()

            with open("static/buffer/profile.png", mode="wb") as curr_img:
                curr_img.write(self.img)
