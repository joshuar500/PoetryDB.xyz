from flask import Flask, render_template, request,\
    redirect, url_for, flash, jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Author, Poem, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///poetryandalcohol.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('/etc/login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if user exists, if it doesn't make a new one
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')

    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


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
    if 'username' not in login_session:
        # there's gotta be a better way than to embed an if statement in the html
        # to prevent users from accessing the edit buttons
        creator = "no-user-sup-widdit"
        print "logged in as" + creator
        return render_template('index.html', authors=authors, creator=creator)
    elif 'username' in login_session:
        creator = login_session['username']
        print "logged in aszzzzzz" + creator
        return render_template('index.html', authors=authors, creator=creator)
    else:
        return redirect('/login')


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


# adds an author to the database
@app.route('/poem/new/', methods=['GET', 'POST'])
def add_poem():
    if request.method == 'POST':
        new_poem_name = request.form['name']
        new_poem_text = request.form['the_poem']
        author_id = request.form['author_id']
        print new_poem_text
        print author_id
        new_poem = Poem(name=new_poem_name,
                        the_poem=new_poem_text,
                        author_id=author_id)
        session.add(new_poem)
        session.commit()
        flash("new poem added")
        return redirect(url_for('back'))
    else:
        # this should return an error on the form
        return render_template('index.html')


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


# deletes an author and all poems from the database
@app.route('/poem/delete/', methods=['GET', 'POST'])
def delete_poem():
    if request.method == 'POST':
        poem_id = request.form['id']
        poem_to_delete = session.query(Poem).filter_by(id=poem_id).one()
        session.delete(poem_to_delete)
        session.commit()

        flash("a poem has been deleted")
        return redirect(url_for('back'))
    else:
        # this should return an error on the form
        return render_template('index.html')


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
