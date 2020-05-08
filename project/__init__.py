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
app.config['SECRET_KEY'] = 'ba8ed3f480b55b599b397e000da63ccf'

# this is the connection to the mysql
# db = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b94531a8a9be0d', password='440412d5', db='heroku_c22f6c727a9c888')

# this function grabs a connection to the mySQL database 
def get_db():
	db = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b94531a8a9be0d', password='440412d5', db='heroku_c22f6c727a9c888')
	return db

# import project routes
from project import routes

