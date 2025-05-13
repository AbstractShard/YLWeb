from sqlalchemy import Table, Column, Integer, ForeignKey
from .db_session import SqlAlchemyBase

user_project_association = Table(
    'user_project_association',
    SqlAlchemyBase.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)