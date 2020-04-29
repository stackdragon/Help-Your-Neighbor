# this contains the classes for each of our main forms using wtforms

from flask_wtf import FlaskForm
from datetime import date, datetime
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms_components import DateRange
import mysql.connector

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	# custom validation to make sure that the username does already exit in the Users table
	def validate_username(self, username):

		# connect to the database
		db = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b94531a8a9be0d', password='440412d5', db='heroku_c22f6c727a9c888')
		mycursor = db.cursor()

		# run query to see if the username is already in the table
		query = f"SELECT userName from Users WHERE userName='{username.data}';"
		mycursor.execute(query)
		user = mycursor.fetchall()

		# display the validation error
		if user:
			raise ValidationError('Username already exists. Please choose a unique username.')
			db.close()

	# custom validation to make sure that the email address does already exit in the Users table
	def validate_email(self, email):
		db = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b94531a8a9be0d', password='440412d5', db='heroku_c22f6c727a9c888')
		mycursor = db.cursor()
		
		query = f"SELECT userEmail from Users WHERE userEmail='{email.data}';"
		mycursor.execute(query)
		user = mycursor.fetchall()

		if user:
			raise ValidationError('Email address already exists in our system. Please enter a unique email address.')

		db.close()

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

class AddForm(FlaskForm):
	item = SelectField('Item Needed', choices = [('tp', 'toilet paper'), ('pt', 'paper towels'), ('aspirin', 'aspirin'), ('milk', 'milk')], validators=[DataRequired()])
	dateNeeded = DateField('Date Needed', default=date.today, validators=[DataRequired(), DateRange(min=date.today())])
	submit = SubmitField('Submit')



