from flask_wtf import FlaskForm
from datetime import date, datetime
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_components import DateRange


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

class AddForm(FlaskForm):
	item = SelectField('Item Needed', choices = [('tp', 'toilet paper'), ('pt', 'paper towels'), ('aspirin', 'aspirin'), ('milk', 'milk')], validators=[DataRequired()])
	dateNeeded = DateField('Date Needed', default=date.today, validators=[DataRequired(), DateRange(min=date.today())])
	submit = SubmitField('Submit')



