from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Author, Poem, Alcohol

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

alcohol1 = Alcohol(name="Whisky")

session.add(alcohol1)
session.commit()

poem1 = Poem(
    name="In a Station of the Metro",
    the_poem="THE apparition of these faces in the crowd;\nPetals on a wet, black bough.",
    alcohol=alcohol1,
    tags="imagery, subtle",
    author=author1,)

session.add(poem1)
session.commit()

alcohol2 = Alcohol(name="Vodka")

session.add(alcohol2)
session.commit()

poem2 = Poem(
    name="A Girl",
    the_poem="The tree has entered my hands,\nThe sap has ascended my arms,\nThe tree has grown in my breast -\nDownward,\nThe branches grow out of me, like arms.\n\nTree you are,\nMoss you are,\nYou are violets with wind above them.\nA child - so high - you are,\nAnd all this is folly to the world. ",
    alcohol=alcohol2,
    tags="imagery, love",
    author=author1,)

session.add(poem2)
session.commit()

alcohol3 = Alcohol(name="Bud Lite")

session.add(alcohol3)
session.commit()

poem3 = Poem(
    name="And the days are not full enough",
    the_poem="And the days are not full enough\nAnd the nights are not full enough\nAnd life slips by like a field mouse\n      Not shaking the grass ",
    alcohol=alcohol3,
    tags="imagery, love",
    author=author1,)

session.add(poem3)
session.commit()

# Author 2
author2 = Author(name="Robert Frost")

session.add(author2)
session.commit()

poem4 = Poem(
    name="The Road Not Taken",
    the_poem='''
Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;

Then took the other, as just as fair,
And having perhaps the better claim
Because it was grassy and wanted wear,
Though as for that the passing there
Had worn them really about the same,

And both that morning equally lay
In leaves no step had trodden black.
Oh, I kept the first for another day!
Yet knowing how way leads on to way
I doubted if I should ever come back.

I shall be telling this with a sigh
Somewhere ages and ages hence:
Two roads diverged in a wood, and I,
I took the one less traveled by,
And that has made all the difference.
    ''',
    alcohol=alcohol1,
    tags="risk",
    author=author2,)

session.add(poem4)
session.commit()

session.close()

print "added menu items!"
