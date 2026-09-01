from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from modules.shared.settings import settings

__engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    Session = sessionmaker(autocommit=False, autoflush=False, bind=__engine)
    with Session() as session:
        yield session
