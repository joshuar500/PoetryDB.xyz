from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Author, Poem


engine = create_engine('sqlite:///poetryandalcohol.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# set up index route
@app.route('/')
@app.route('/authors/')
def authors():
    authors = session.query(Author).all()
    return render_template('index.html', authors=authors)


# queries all authors and returns JSON
@app.route('/authors/JSON')
def authors_JSON():
    authors = session.query(Author).all()
    return jsonify(Authors=[a.serialize for a in authors])


# adds an author to the database
@app.route('/authors/new/', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        newAuthor = Author(name=request.form['name'])
        session.add(newAuthor)
        session.commit()
        flash("new author created")
        return redirect(url_for('back'))
    else:
        # this should return an error on the form
        return render_template('index.html')


# redirects the user to the index page
@app.route('/back')
def back():
    this_url = 'authors'
    if this_url is None:
        return redirect(url_for('authors'))
    else:
        return redirect(this_url)


# returns a list of the authors poems in json format
# list is updated via jquery getJSON
@app.route('/get_author_poems')
def get_author_poems():
    author_id = request.args.get('author_id', 0, type=int)
    author = session.query(Author).filter_by(id=author_id).one()
    poems = session.query(Poem).filter_by(author_id=author.id).all()
    return jsonify(Poems=[p.serialize for p in poems])


# returns a single poem in json for jquery update
@app.route('/get_poem')
def get_poem():
    print "IM HERE"
    poem_id = request.args.get('poem_id', 0, type=int)
    poem = session.query(Poem).filter_by(id=poem_id).one()
    return jsonify(Poem=poem.serialize)


@app.route(
    '/authors/<int:author_id>/<int:poem_id>/edit',
    methods=['GET', 'POST'])
def edit_poem(author_id, poem_id):
    editedPoem = session.query(Poem).filter_by(id=poem_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedPoem.name = request.form['name']
        session.add(editedPoem)
        session.commit()
        flash("a poem has been edited")
        return redirect(url_for('authors_poems', author_id=author_id))
    else:
        return render_template(
            'editpoem.html',
            author_id=author_id,
            poem_id=poem_id, i=editedPoem)


@app.route(
    '/authors/<int:author_id>/<int:poem_id>/delete',
    methods=['GET', 'POST'])
def delete_poem(author_id, poem_id):
    poemToDelete = session.query(Poem).filter_by(id=poem_id).one()
    if request.method == 'POST':
        session.delete(poemToDelete)
        session.commit()
        flash("a poem has been deleted")
        return redirect(url_for('authors_poems', author_id=author_id))
    else:
        return render_template(
            'deletepoem.html',
            i=poemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
