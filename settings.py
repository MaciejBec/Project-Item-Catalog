import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://udacity:udacity@localhost/udacity'
db = SQLAlchemy(app)
