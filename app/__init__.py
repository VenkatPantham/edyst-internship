from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_simple import JWTManager
from flask_bcrypt import Bcrypt
import os

# Initializing App
app = Flask(__name__)

# for validating an Admin 
regex = '^[a-z0-9]+[\._]?[a-z0-9]+@edyst.com$'

basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+ os.path.join(
    basedir, "../db.sqlite"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_SECRET_KEY'] = 'edyst-secret'
app.config['JSON_SORT_KEYS'] = False    

# Initializing Database
db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

from app import routes