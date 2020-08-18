# import mysql connector module
import mysql.connector

#import json python module
import json

# import bcrypt for password hashing
from flask_bcrypt import Bcrypt

# import flask-login for session management
from flask_login import LoginManager

# import Flask
from flask import Flask

# name of webapp
app = Flask(__name__)

# create bcrpyt class object for password hashing
bcrypt = Bcrypt(app)

#  create flask-login class object for session management
login_manager = LoginManager(app)

# if user tries to access a page requiring a login, revert to 'login' route
# and error message should have the boostrap 'info' css class
login_manager.login_message_category = 'info'
login_manager.login_view = 'login'



# this is a CSRF token for security (required for WTForms)
app.config['SECRET_KEY'] = 'XXX'

# this is the connection to the mysql
# XXX

# this function grabs a connection to the mySQL database 
def get_db():
	db = mysql.connector.connect(host='XXX', user='XXX', password='XXX', db='XXX')
	return db

# import project routes
from project import routes

