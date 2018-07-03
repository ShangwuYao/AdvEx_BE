import os
from datetime import datetime
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
     ForeignKey, event
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

# from config.testing_local import *
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']


engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Model = declarative_base(name='Model')
Model.query = db_session.query_property()

def init_db():
    Model.metadata.create_all(bind=engine)


class User(Model):
    """
    access attribute by someuser.user_id
    """
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    nickname = Column(String(200), unique=False, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password = Column(String(200), unique=False, nullable=False)

    def __repr__(self):
        return '<User id: {}, nickname: {}, email: {}>'.format(self.user_id, 
            self.nickname, self.email)


class Submission(Model):
    __tablename__ = 'submission'
    submission_id = Column(Integer, primary_key=True)
    model_name = Column(String(80), nullable=False)
    status = Column(String(80), nullable=False)
    s3_model_key = Column(String(80), nullable=False)
    s3_index_key = Column(String(80), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    feedback = Column(JSON, nullable=True)

    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    
    user = relationship('User',
        backref=backref('submission', lazy=True), uselist=False)

    def __repr__(self):
        return '<Submission: {}>'.format(self.submission_id)


