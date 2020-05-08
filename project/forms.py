# this contains the classes for each of our main forms using wtforms

from flask_wtf import FlaskForm
from datetime import date, datetime
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField
from wtforms.fields.html5 import DateField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from wtforms_components import DateRange
from project import get_db
import mysql.connector

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
	lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
	userStreet = StringField('Street Address', validators=[DataRequired(), Length(min=2, max=50)])
	userCity = StringField('City', validators=[DataRequired(), Length(min=2, max=30)])
	userState = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
	userZip = StringField('Zip Code', validators=[DataRequired(), Length(min=5, max=5)])
	#is there a way to validate specific chars?
	userPhone = StringField('Phone Number', validators=[DataRequired(), Length(min=12, max=12)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	# custom validation to make sure that the username doesn't already exist in the Users table
	def validate_username(self, username):

		db = get_db()

		mycursor = db.cursor()

		# run query to see if the username is already in the table
		query = f"SELECT userName from Users WHERE userName='{username.data}';"
		mycursor.execute(query)
		user = mycursor.fetchall()
		mycursor.close()

		# display the validation error
		if user:
			raise ValidationError('Username already exists. Please choose a unique username.')

	# custom validation to make sure that the email address does already exit in the Users table
	def validate_email(self, email):
		db = get_db()
		mycursor = db.cursor()
		
		query = f"SELECT userEmail from Users WHERE userEmail='{email.data}';"
		mycursor.execute(query)
		user = mycursor.fetchall()
		mycursor.close()

		if user:
			raise ValidationError('Email address already exists in our system. Please enter a unique email address.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

class AddForm(FlaskForm):
	autocomp = StringField('Item', id='item_autocomplete')
	qty = IntegerField('Quantity', id='qty')
	dateNeeded = DateField('Request Needed By', default=date.today, validators=[DateRange(min=date.today())])
	dateRequested = HiddenField(default=date.today)
	specialInstructions = StringField('Special Instructions (if any)', validators=[Optional(), Length(min=2, max=200)])
	itemsAdded = HiddenField('itemsAdded', default="", id="hiddenItems", validators=[DataRequired(message="A request needs to include at least 1 item")]) # used for validating whether any items have been added to the request
	quantitiesAdded = HiddenField('quantitiesAdded', default="", id="hiddenQuantities")
	submit = SubmitField('Submit Request')

class UpdateForm(FlaskForm):
	firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
	lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
	userStreet = StringField('Street Address', validators=[DataRequired(), Length(min=2, max=50)])
	userCity = StringField('City', validators=[DataRequired(), Length(min=2, max=30)])
	userState = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
	userZip = StringField('Zip Code', validators=[DataRequired(), Length(min=5, max=5)])
	#is there a way to validate specific chars?
	userPhone = StringField('Phone Number', validators=[DataRequired(), Length(min=12, max=12)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Update')
	#HOW TO WE ALLOW CURRENT EMAIL TO PERSIST BUT ALSO VERIFY NOT ALREADY IN SYSTEM FOR SOMEONE ELSE?

class DeleteRequestForm(FlaskForm):
	requestID = HiddenField('Request ID')
	submit = SubmitField('Delete Request')

class DeleteFulfillmentForm(FlaskForm):
	fulfillmentID = HiddenField('Fulfillment ID')
	submit = SubmitField('Delete Fulfillment')

class SearchForm(FlaskForm):
	searchZip = StringField('Find Requests by Zip Code', validators=[DataRequired()])
	submit = SubmitField('Search')

class cartForm(FlaskForm):
	submit = SubmitField('Checkout')