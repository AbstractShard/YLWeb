import consts
import sqlalchemy as sa
import sqlalchemy.orm as orm

from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()
factory = None


def global_init(db_file_path: str = None):
    global factory

    if factory:
        return

    # Получаем строку подключения из переменной окружения
    db_url = consts.DATABASE_URL
    if db_url:
        conn_str = db_url
    else:
        raise Exception("Нужен PostgreSQL URL")

    engine = sa.create_engine(
        conn_str,            # Используем URL из переменной окружения
        echo=False,          # Отключаем вывод SQL-запросов в консоль
        pool_size=5,         # Максимум 5 одновременных соединений (можно меньше)
        max_overflow=2,      # Дополнительные соединения при пике нагрузки
        pool_recycle=1800,   # Пересоздавать соединение каждые 30 минут
        pool_pre_ping=True   # Проверять соединение перед использованием
    )
    factory = orm.sessionmaker(bind=engine)

    from . import all_modules

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global factory
    return factory()
