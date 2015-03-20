from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Author, Poem

# #Fake authors
# restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

# authors = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


# #Fake Menu Items
# items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
# item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

engine = create_engine('sqlite:///poetryandalcohol.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Making an API Endpoint (GET request)
@app.route('/authors/<int:author_id>/poems/JSON')
def restaurant_menu_JSON(author_id):
    author = session.query(Author).filter_by(id=author_id).one()
    poems = session.query(Poem).filter_by(author_id=author.id).all()
    return jsonify(MenuItems=[p.serialize for p in poems])


@app.route('/authors/<int:author_id>/poems/<int:poem_id>/JSON')
def menu_item_JSON(restaurant_id, poem_id):
    poem = session.query(Poem).filter_by(id=poem_id).one()
    return jsonify(Poem=poem.serialize)

@app.route('/')
@app.route('/authors/')
def authors():
    authors = session.query(Author).all()
    return render_template('index.html', authors=authors)

@app.route('/authors/<int:author_id>/')
def restaurant_menu(author_id):
    author = session.query(Author).filter_by(id=author_id).one()
    poems = session.query(Poem).filter_by(author_id=author.id)
    return render_template('menu.html', author=author, poems=poems)


@app.route(
    '/authors/<int:author_id>/new',
    methods=['GET', 'POST'])
def new_menu_item(author_id):
    if request.method == 'POST':
        newPoem = Poem(name=request.form['name'], author_id=author_id)
        session.add(newPoem)
        session.commit()
        flash("new poem created")
        return redirect(url_for('restaurant_menu', author_id=author_id))
    else:
        return render_template('newmenuitem.html', author_id=author_id)


@app.route(
    '/authors/<int:author_id>/<int:poem_id>/edit',
    methods=['GET', 'POST'])
def edit_menu_item(author_id, poem_id):
    editedPoem = session.query(Poem).filter_by(id=poem_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedPoem.name = request.form['name']
        session.add(editedPoem)
        session.commit()
        flash("a poem has been edited")
        return redirect(url_for('restaurant_menu', author_id=author_id))
    else:
        return render_template(
            'editmenuitem.html',
            author_id=author_id,
            poem_id=poem_id, i=editedPoem)


@app.route(
    '/authors/<int:author_id>/<int:poem_id>/delete',
    methods=['GET', 'POST'])
def delete_menu_item(author_id, poem_id):
    poemToDelete = session.query(Poem).filter_by(id=poem_id).one()
    if request.method == 'POST':
        session.delete(poemToDelete)
        session.commit()
        flash("a poem has been deleted")
        return redirect(url_for('restaurant_menu', author_id=author_id))
    else:
        return render_template(
            'deletemenuitem.html',
            i=poemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
