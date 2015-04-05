from flask import Flask, render_template, request,\
    redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Author, Poem

app = Flask(__name__)

engine = create_engine('sqlite:///poetryandalcohol.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# redirects the user to the index page
@app.route('/back')
def back():
    this_url = ''
    if this_url is None:
        return redirect(url_for(''))
    else:
        return redirect(this_url)


# set up index route
@app.route('/')
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
        new_author = Author(name=request.form['name'])
        session.add(new_author)
        session.commit()
        flash("new author created")
        return redirect(url_for('back'))
    else:
        # this should return an error on the form
        return render_template('index.html')


# updates an authors name in the database
@app.route('/authors/update/', methods=['GET', 'POST'])
def update_author():
    if request.method == 'POST':
        new_name = request.form['name']
        author_id = request.form['id']

        editedAuthor = session.query(Author).filter_by(id=author_id).one()
        editedAuthor.name = new_name

        session.add(editedAuthor)
        session.commit()
        flash("author name updated")
        return redirect(url_for('back'))
    else:
        # this should return an error on the form
        return render_template('index.html')


# deletes an author and all poems from the database
@app.route('/authors/delete/', methods=['GET', 'POST'])
def delete_author():
    if request.method == 'POST':
        author_id = request.form['id']
        author_to_delete = session.query(Author).filter_by(id=author_id).one()
        session.delete(author_to_delete)
        session.commit()
        # delete all poems associated with author
        author_poems = session.query(Poem).filter_by(author_id=author_id).all()
        session.delete(author_poems)
        session.commit()
        flash("an author has been deleted")
        return redirect(url_for('back'))
    else:
        # this should return an error on the form
        return render_template('index.html')


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


# updates a poem by a specific author
@app.route('/poem/update/', methods=['GET', 'POST'])
def update_poem():
    if request.method == 'POST':
        new_name = request.form['name']
        new_poem = request.form['the_poem']
        poem_id = request.form['id']

        editedPoem = session.query(Poem).filter_by(id=poem_id).one()
        editedPoem.name = new_name
        editedPoem.the_poem = new_poem

        session.add(editedPoem)
        session.commit()
        flash("poem name/entry updated")
        return redirect(url_for('back'))
    else:
        # this should return an error on the form
        return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
