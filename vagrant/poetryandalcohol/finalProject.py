from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Author, Poem


engine = create_engine('sqlite:///poetryandalcohol.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Making an API Endpoint (GET request)
@app.route('/authors/JSON')
def authors_JSON():
    authors = session.query(Author).all()
    return jsonify(Authors=[a.serialize for a in authors])


@app.route('/authors/<int:author_id>/poems/JSON')
def authors_poems_JSON(author_id):
    author = session.query(Author).filter_by(id=author_id).one()
    poems = session.query(Poem).filter_by(author_id=author.id).all()
    return jsonify(Poems=[p.serialize for p in poems])


@app.route('/get_author_poems')
def get_author_poems():
    author_id = request.args.get('author_id', 0, type=int)
    author = session.query(Author).filter_by(id=author_id).one()
    poems = session.query(Poem).filter_by(author_id=author.id).all()
    return jsonify(Poems=[p.serialize for p in poems])


@app.route('/authors/<int:author_id>/poems/<int:poem_id>/JSON')
def menu_item_JSON(author_id, poem_id):
    poem = session.query(Poem).filter_by(id=poem_id).one()
    return jsonify(Poem=poem.serialize)

# TODO: Change this back to authors.html
@app.route('/')
@app.route('/authors/')
def authors():
    authors = session.query(Author).all()
    return render_template('index.html', authors=authors)


@app.route('/authors/<int:author_id>/')
def authors_poems(author_id):
    author = session.query(Author).filter_by(id=author_id).one()
    poems = session.query(Poem).filter_by(author_id=author.id)
    return render_template('poems.html', author=author, poems=poems)


@app.route('/authors/<int:author_id>/<int:poem_id>')
def view_poem(author_id, poem_id):
    author = session.query(Author).filter_by(id=author_id).one()
    the_poem = session.query(Poem).filter_by(id=poem_id).one()
    return render_template('viewpoem.html',
        author=author,
        the_poem=the_poem)


@app.route(
    '/authors/<int:author_id>/new',
    methods=['GET', 'POST'])
def new_poem(author_id):
    if request.method == 'POST':
        newPoem = Poem(name=request.form['name'], author_id=author_id)
        session.add(newPoem)
        session.commit()
        flash("new poem created")
        return redirect(url_for('authors_poems', author_id=author_id))
    else:
        return render_template('newpoem.html', author_id=author_id)


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
