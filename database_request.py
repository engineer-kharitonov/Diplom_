import os
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

SQLsystem = 'postgresql'
login = 'postgres'
password = os.getenv("PASSWORD")
host = 'localhost'
port = 5432
db_name = os.getenv("db_name")
DSN = f'{SQLsystem}://{login}:{password}@{host}:{port}/{db_name}'

engine = create_engine(DSN)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    state = Column(String, default='default')

    search_age_from = Column(Integer, default=18)
    search_age_to = Column(Integer, default=45)

    search_sex = Column(Integer, default=0)
    search_city = Column(String, default=None)
    search_status = Column(Integer, default=6)

    current_page = Column(String)
    user_views = relationship('Views', back_populates='user')

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return "<User('%s')>" % self.user_id


class Views(Base):
    __tablename__ = 'views'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    view_id = Column(Integer)
    user = relationship(User, back_populates='user_views')

    def __init__(self, user_id, view_id):
        self.user_id = user_id
        self.view_id = view_id

    def get(self):
        return self.view_id


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
