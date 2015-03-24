from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Author, Poem

engine = create_engine('sqlite:///poetryandalcohol.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Author 1
author1 = Author(name="Ezra Pound")

session.add(author1)
session.commit()

poem1 = Poem(
    name="In a Station of the Metro",
    the_poem='''THE apparition of these faces in the crowd;\n
                Petals on a wet, black bough.''',
    alcohol="Scotch",
    tags="imagery, subtle",
    author=author1)

session.add(poem1)
session.commit()


print "added menu items!"
