from sqlalchemy import create_engine
from db_models import Base
from VARIABLES import DATABASE_URI


engine = create_engine(DATABASE_URI)

def create_tables(drop_previous=False):
    if drop_previous:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        drop_previous = sys.argv[1].lower() == 'drop'
    else:
        drop_previous = False

    create_tables(drop_previous=drop_previous)
