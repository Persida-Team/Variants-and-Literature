from sqlalchemy import create_engine
from model import Base
from enum_and_constants import DATABASE_URI
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


def create_tables(drop_previous=False, db_url=DATABASE_URI):
    engine = create_engine(db_url)
    if drop_previous:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=True)


@contextmanager
def get_session(db_url=DATABASE_URI):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    except Exception:
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        drop_previous = sys.argv[1].lower() == "drop"
    else:
        drop_previous = False

    create_tables(drop_previous=drop_previous)
