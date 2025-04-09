import sqlalchemy as sa
import sqlalchemy.orm as orm

from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()
factory = None


def global_init(db_file_path: str):
    global factory

    if factory:
        return

    if not db_file_path.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f"sqlite:///{db_file_path.strip()}?check_same_thread=False"

    engine = sa.create_engine(conn_str, echo=False)
    factory = orm.sessionmaker(bind=engine)

    from . import all_modules

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global factory
    return factory()
