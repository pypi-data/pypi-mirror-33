from contextlib import contextmanager

from sqlalchemy import create_engine, Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import DB_PATH


eng = create_engine('sqlite:///' + DB_PATH)
session_factory = sessionmaker(bind=eng)
sess = scoped_session(session_factory)
Base = declarative_base()

"""
class Movies(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column('title', String, nullable=True)
    ffmpeg_end_str = Column('ffmpeg_end_str', String, nullable=True)
    ratingKey = Column('ratingKey', Integer)
    prettyname = Column('prettyname', String, nullable=True)
    duration = Column('duration', Integer)
    type = Column('type', String)
    location = Column('location', String, nullable=True)
    updatedAt = Column('updatedAt ', DateTime, nullable=True)
    credits_start = Column('credits_start', Integer, nullable=True)
    credits_start_str = Column('credits_start_str', String, nullable=True)
    correct_credits_start = Column('correct_credits_start', Integer, nullable=True)
    correct_credits_end = Column('correct_credits_end', Integer, nullable=True)
    credits_end = Column('credits_end', Integer, nullable=True)
    credits_end_str = Column('credits_end_str', String, nullable=True)
    ffmpeg_end = Column('ffmpeg_end', Integer, nullable=True)
    correct_ffmpeg = Column('correct_ffmpeg', Integer, nullable=True)  # This for manual override.

    def _to_tuple(self, keys=None):
        if keys is None:
            keys = [i for i in self.__dict__.keys() if not i.startswith('_')]

        return tuple(getattr(self, i) for i in keys)
"""


class Processed(Base):
    """Table for preprocessed stuff."""
    __tablename__ = "preprocessed"

    id = Column(Integer, primary_key=True)
    show_name = Column('show_name', String, nullable=True)
    title = Column('title', String, nullable=True)
    type = Column('type', String)
    ratingKey = Column('ratingKey', Integer)
    theme_end = Column('theme_end', Integer, nullable=True)
    theme_end_str = Column('theme_end_str', String, nullable=True)
    theme_start = Column('theme_start', Integer, nullable=True)
    theme_start_str = Column('theme_start_str', String, nullable=True)
    correct_theme_start = Column('correct_theme_start', Integer, nullable=True)  # This for manual override.
    correct_theme_end = Column('correct_theme_end', Integer, nullable=True)  # This for manual override.
    prettyname = Column('prettyname', String, nullable=True)
    duration = Column('duration', Integer, nullable=True)
    grandparentRatingKey = Column('grandparentRatingKey', Integer, nullable=True)
    location = Column('location', String, nullable=True)
    updatedAt = Column('updatedAt ', DateTime, nullable=True)
    has_recap = Column('has_recap', Boolean, nullable=True)
    credits_start = Column('credits_start', Integer, nullable=True)
    credits_start_str = Column('credits_start_str', String, nullable=True)
    correct_credits_start = Column('correct_credits_start', Integer, nullable=True)
    correct_credits_end = Column('correct_credits_end', Integer, nullable=True)
    credits_end = Column('credits_end', Integer, nullable=True)
    credits_end_str = Column('credits_end_str', String, nullable=True)
    ffmpeg_end = Column('ffmpeg_end', Integer, nullable=True)
    ffmpeg_end_str = Column('ffmpeg_end_str', String, nullable=True)
    correct_ffmpeg = Column('correct_ffmpeg', Integer, nullable=True)  # This for manual override.

    def _to_tuple(self, keys=None):
        if keys is None:
            keys = [i for i in self.__dict__.keys() if not i.startswith('_')]

        return tuple(getattr(self, i) for i in keys)


# Create db.
Base.metadata.create_all(eng)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = sess()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
