from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from VGTUcoin.blockchain import *
from textwrap import dedent
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Help me pls'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
loginManager = LoginManager(app)
loginManager.login_view = 'login'
loginManager.login_message_category = 'info'
# Sugeneruoti globalu unikalu adresa
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchainObj = Blockchain()

from VGTUcoin import FlaskRoutes;
