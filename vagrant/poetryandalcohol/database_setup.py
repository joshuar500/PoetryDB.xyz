from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

# Create base class that our classes will inherit
Base = declarative_base()


class Author(Base):

    __tablename__ = 'author'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class Poem(Base):

    __tablename__ = 'poem'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    the_poem = Column(String(250))
    alcohol = Column(String(80))
    tags = Column(String(80))
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship(Author)

    @property
    def serialize(self):
        # Returns an object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
            'the_poem': self.description,
            'alcohol': self.price,
            'tags': self.course,
            'author': self.author,
        }


engine = create_engine('sqlite:///poetryandalcohol.db')

# Goes into database and adds all our stuff
Base.metadata.create_all(engine)
