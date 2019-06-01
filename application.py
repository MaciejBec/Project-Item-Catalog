import json
import secrets
from collections import defaultdict
from functools import wraps

import requests
from flask import render_template, request, make_response, session, \
    jsonify, url_for
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from werkzeug.utils import redirect

from forms import Itemform
from models import Item, Category
# Get google client_id for this app from json file
from settings import app, db

with open('client_secrets.json', 'r') as f:
    CLIENT_ID = json.load(f)['web']['client_id']


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user_google_id'):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


@app.route('/logout', methods=["POST"])
def logout():
    session.pop('access_token', None)
    session.pop('user_google_id', None)
    session.pop('username', None)
    session.pop('picture', None)
    session.pop('email', None)
    session.pop('username', None)
    return "Success"


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        state = secrets.token_hex(32)
        session['state'] = state
        return render_template('login.html', STATE=state)
    else:
        # Check the state variable for extra security
        if session['state'] != request.args.get('state'):
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Retrieve the token sent by the client
        token = request.data

        # Request an access token from the google api
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), CLIENT_ID)
        url = 'https://oauth2.googleapis.com/tokeninfo?id_token=%s' % \
              token.decode(encoding='utf-8')
        result = requests.get(url).json()

        # If there was an error in the access token info, abort.
        if result.get('error'):
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is used for the intended user.
        user_google_id = idinfo['sub']
        if result['sub'] != user_google_id:
            response = make_response(json.dumps(
                "Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for this app.
        if result['aud'] != CLIENT_ID:
            response = make_response(json.dumps(
                "Token's client ID does not match app's."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check if the user is already logged in
        stored_access_token = session.get('access_token')
        stored_user_google_id = session.get('user_google_id')
        if stored_access_token and user_google_id == stored_user_google_id:
            response = make_response(json.dumps(
                'Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        session['access_token'] = idinfo
        session['user_google_id'] = user_google_id
        # Get user info
        session['username'] = idinfo['name']
        session['picture'] = idinfo['picture']
        session['email'] = idinfo['email']

        return make_response(json.dumps('Success'), 200)


@app.route("/")
def home():
    items = Item.query.limit(10)
    categories = Category.query.all()
    return render_template("home.html", categories=categories, items=items)


@app.route("/catalog.json")
def catalog_json():
    data = defaultdict(list)
    categories = Category.query.all()
    for category in categories:
        data['category'].append(category.serialize)
    return jsonify(data)

@app.route("/category/<string:name>.json")
def category_json(name):
    data = defaultdict(list)
    category = Category.query.filter(Category.name == name).first()
    for item in category.items:
        data['items'].append(item.serialize)
    return jsonify(data)

@app.route("/category/<string:category>")
def category_view(category):
    category = Category.query.filter(Category.name == category).first()
    items = category.items
    return render_template("category.html", category=category, items=items)


@app.route("/add-item", methods=["GET", "POST"])
@login_required
def add_item():
    form = Itemform()
    form.cat_id.choices = [(cat.id, cat.name) for cat in Category.query.all()]
    if form.validate_on_submit():
        item_new = Item(cat_id=form.data.get('cat_id'),
                        description=form.data.get('description'),
                        title=form.data.get('title'),
                        author=session.get('user_google_id')
                        )

        db.session.add(item_new)
        db.session.commit()

        return redirect('/')
    return render_template("add_item.html", form=form)


@app.route("/category/<string:category>/<string:title>/edit-item",
           methods=["GET", "POST"])
@login_required
def edit_item(category, title):
    cat = Category.query.filter(Category.name == category).first()
    item = Item.query.filter(
        Item.cat_id == cat.id, Item.title == title).first()

    if session.get('user_google_id') != item.author:
        return redirect(url_for('home'))

    form = Itemform(request.form, obj=item)
    form.cat_id.choices = [(cat.id, cat.name) for cat in Category.query.all()]
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.add(item)
        db.session.commit()

        return redirect('/category/{}'.format(category))
    return render_template("add_item.html", form=form)


@app.route("/category/<string:category>/<string:title>")
def item_view(category, title):
    cat = Category.query.filter(Category.name == category).first()
    item = Item.query.filter(
        Item.title == title, Item.cat_id == cat.id).first()
    return render_template("item.html", item=item)


@app.route("/category/<string:category>/<string:title>/delete",
           methods=["GET", "POST"])
@login_required
def item_del(category, title):
    cat = Category.query.filter(Category.name == category).first()
    item = Item.query.filter(
        Item.title == title, Item.cat_id == cat.id).first()
    if session.get('user_google_id') != item.author:
        return redirect(url_for('home'))

    if request.method == "POST":
        if int(request.form.get("del")):
            db.session.delete(item)
            db.session.commit()
            return redirect('/')
        else:
            return redirect('/')
    return render_template("delete.html", item=item)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == "__main__":
    app.debug = True
    app.run(host="localhost", port=5000, threaded=False)
