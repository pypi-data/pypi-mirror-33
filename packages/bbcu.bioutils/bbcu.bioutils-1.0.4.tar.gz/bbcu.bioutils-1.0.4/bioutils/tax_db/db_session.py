from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from settings import DB


class Session(object):
    def __init__(self, db=DB, pool_recycle=60):
        engine = create_engine(db, pool_recycle=pool_recycle)
        session_workspace = sessionmaker(bind=engine)
        self.session = session_workspace()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()
