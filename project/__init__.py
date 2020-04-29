# import mysql connector module
import mysql.connector

# import bcrypt for password hashing
from flask_bcrypt import Bcrypt

# import flask-login for session management
#from flask_login import LoginManager

# import Flask
from flask import Flask

# name of webapp
app = Flask(__name__)

# create bcrpyt class object for password hashing
bcrypt = Bcrypt(app)

#create flask-login class object for session management
# login_manager = LoginManager(app)

# this is a CSRF token for security (required for WTForms)
app.config['SECRET_KEY'] = 'ba8ed3f480b55b599b397e000da63ccf'

# this is the connection to the mysql
db = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b94531a8a9be0d', password='440412d5', db='heroku_c22f6c727a9c888')

# import project routes
from project import routes

