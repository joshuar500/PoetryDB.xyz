from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

# Create base class that our classes will inherit
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    
    @property
    def serialize(self):
        # Returns an object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
        }


class Author(Base):

    __tablename__ = 'author'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns an object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
        }


class Alcohol(Base):

    __tablename__ = 'alcohol'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns an object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
        }


class Poem(Base):

    __tablename__ = 'poem'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    the_poem = Column(String(250))
    tags = Column(String(80))
    alcohol_id = Column(Integer, ForeignKey('alcohol.id'))
    alcohol = relationship(Alcohol)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship(Author)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns an object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
            'the_poem': self.the_poem,
            'tags': self.tags,
            'alcohol_id': self.alcohol_id,
            'author_id': self.author_id,
            'user_id': self.user_id,            
        }


engine = create_engine('sqlite:///poetryandalcohol.db')

# Goes into database and adds all our stuff
Base.metadata.create_all(engine)
