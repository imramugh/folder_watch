from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
import os

Base = declarative_base()

class File(Base):
    __tablename__ = 'Files'

    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    date_modified = Column(DateTime, nullable=False)
    embedded = Column(Boolean, default=False)

def setup_database():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'folder_watch.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

if __name__ == '__main__':
    setup_database()