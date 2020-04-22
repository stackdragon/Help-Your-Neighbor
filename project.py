# import mysql connector module
import mysql.connector

#import modules for Flask, rendering templates, message display, and url generation
from flask import Flask, render_template, url_for, flash, redirect

#wtForm classes for registration and login forms
from forms import RegistrationForm, LoginForm, AddForm

app = Flask(__name__)

# this is a CSRF token for security -->
app.config['SECRET_KEY'] = 'ba8ed3f480b55b599b397e000da63ccf'

#home page route
@app.route('/')
@app.route('/home')
def home():
		return render_template('home.html')

#about page route
@app.route('/about')
def about():
    return render_template('about.html')

#registration page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

    	# display success message if user successfully registered
    	flash(f'Account created for {form.username.data}!', 'success')
    	return redirect(url_for('home'))
    return render_template('register.html', title='Register', form = form)

#add page route
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        #display success message if request successfully added

        # grab the value of the item
        value = dict(form.item.choices).get(form.item.data)
        flash(f'You created a request for {value} to be provided by {form.dateNeeded.data}.', 'success')
        return redirect(url_for('home'))
    return render_template('add.html', title='Make Your Request', form = form)

# login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

    	# display success message if user successfully logs in
    	if form.email.data == 'test' and form.password.data == 'password':
    		flash('You are now logged in!', 'success')
    		return redirect(url_for('home'))
    	else:
    		flash('Username and password combination not found. Please try again.', 'danger')
    return render_template('login.html', title='Login', form = form)


# app will run in debug mode if run from terminal
if __name__ == '__main__':
    app.run(debug=True)
