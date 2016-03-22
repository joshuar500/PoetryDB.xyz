from flask import Flask, render_template, request,\
    redirect, url_for, flash, jsonify, make_response
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Author, Poem, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
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


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data    

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
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

    flash("Now logged in as %s" % login_session['username'])
    return output
        

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        print "THE INVALID BITCH NIGGAA"
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

    login_session['provider'] = 'google'
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


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    return "you have been logged out" 
    

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = AccessTokenCredentials(login_session['credentials'],
                                         'user-agent-value')    
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
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
        if 'admin' in login_session:
            del login_session['admin']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        # Change this because of P3P policy. Stupid fucking thing.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
        
        
# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    print "disconnectingghakljshd"
    if 'provider' in login_session:
        print "next"
        if login_session['provider'] == 'google':
            print "gdisconnect"
            gdisconnect()
            flash("You have successfully been logged out.")
            return redirect(url_for('authors'))
        if login_session['provider'] == 'facebook':
            print "fbdisconnect"
            fbdisconnect()            
            flash("You have successfully been logged out.")
            return redirect(url_for('authors'))
    else:
        flash("You were not logged in")
        return redirect(url_for('authors'))        


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
    #Create State
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    print state
    login_session['state'] = state
    authors = session.query(Author).all()
    if 'email' not in login_session:        
        print "EMAISDLKASHF"
        return render_template('index.html', authors=authors, STATE=state)
    elif 'email' in login_session:
        user_id = getUserId(login_session['email'])
        creator = login_session['email']
        return render_template('index.html', authors=authors, STATE=state, creator=creator, user_id=user_id)
    else:
        return redirect('/login')
        
# returns logged in users id        
@app.route('/get_current_user')
def get_current_user():
    try:
        user_id = getUserId(login_session['email'])
        return jsonify(user_id=user_id)
    except:
        return render_template('index.html', user_id=0)
        
# get and return search terms
@app.route('/get_search_term', methods=['GET'])
def get_search_term():    
    term = request.args.get('q')
    do_query_authors = session.query(Author.name).filter(Author.name.like('%' + str(term) + '%'))
    do_query_poems = session.query(Poem.name).filter(Poem.name.like('%' + str(term) + '%'))
    author_results = [author[0] for author in do_query_authors.all()]
    poem_results = [poem[0] for poem in do_query_poems.all()]        
    #print author_results
    #print poem_results
    return jsonify(search_term=author_results)
    

# adds an author to the database
@app.route('/authors/new/', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        #if author exists, do not create new author
        all_authors = session.query(Author).all()
        new_author = request.form['name']
        #fix this for multiple rows check        
        exists = session.query(Author.name).filter_by(name=new_author).scalar() is not None
        print new_author
        print new_author
        print new_author
        print new_author
        if exists:
            print "Author exists widdit"
            return redirect(url_for('back'))
        else:
            new_author = Author(name=new_author, user_id=getUserId(login_session['email']))            
            session.add(new_author)
            session.commit()
            print "Author CREATED"            
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
        
        print new_name
        print author_id

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
        # delete all poems associated with author if they exist
        try:
            author_poems = session.query(Poem).filter_by(author_id=author_id).all()
            session.delete(author_poems)
            session.commit()
            return redirect(url_for('back'))
        except:           
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
    poem_id = request.args.get('poem_id', 0, type=int)
    poem = session.query(Poem).filter_by(id=poem_id).one()
    return jsonify(Poem=poem.serialize)


# adds an author to the database
@app.route('/poem/new/', methods=['GET', 'POST'])
def add_poem():
    if request.method == 'POST':        
        new_poem_name = request.form['poemTitle']
        new_poem_text = request.form['poemText']
        author_name = request.form['name']
        user_id = getUserId(login_session['email'])
        try:        
            if session.query(Author).filter_by(name=author_name).one() is not None:                
                author = session.query(Author).filter_by(name=author_name).one()
                author_id = author.id
                new_poem = Poem(name=new_poem_name,
                                the_poem=new_poem_text,
                                author_id=author_id,
                                user_id=user_id)
                session.add(new_poem)
                session.commit()
                return redirect(url_for('back'))
        except:            
            print "FIX IF THERE IS NO AUTHOR, WHAT DO TO IN THIS EXCEPT CASE????"
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


#########
#### API ENDPOINTS
#########

# queries all authors and returns JSON
@app.route('/authors/JSON')
def authors_JSON():
    authors = session.query(Author).all()
    return jsonify(Authors=[a.serialize for a in authors])
    
@app.route('/authors/<int:author_id>/poems/JSON')
def authors_poems_JSON(author_id):
    poems = session.query(Poem).filter_by(author_id=author_id)
    return jsonify(Poem=[p.serialize for p in poems])
        
# @app.route('/authors/<int:author_id>/poems/<int:poem_id>/JSON')
# def poem_JSON():
#     authors = session.query(Author).all()
#     return jsonify(Authors=[a.serialize for a in authors])


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
