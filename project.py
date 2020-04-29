# import mysql connector module
import mysql.connector

# import bcrypt for password hashing
from flask_bcrypt import Bcrypt

# import modules for Flask, rendering templates, message display, and url generation
from flask import Flask, render_template, url_for, flash, redirect

# import wtForm classes for registration and login forms
from forms import RegistrationForm, LoginForm, AddForm

# name of webapp
app = Flask(__name__)

# create bcrpyt class object for password hashing
bcrypt = Bcrypt(app)

# this is a CSRF token for security -->
app.config['SECRET_KEY'] = 'ba8ed3f480b55b599b397e000da63ccf'

#home page route
@app.route('/')
@app.route('/home')
def home():

    # connect to the database
    db = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b94531a8a9be0d', password='440412d5', db='heroku_c22f6c727a9c888')
    
    # set up db cursor
    mycursor = db.cursor()

    mycursor.execute("""DROP TABLE IF EXISTS diagnostic;""")
    mycursor.execute("""CREATE TABLE diagnostic(id INT PRIMARY KEY, text VARCHAR(255) NOT NULL);""")
    mycursor.execute("""INSERT INTO diagnostic (text) VALUES ("MySQL is working");""")
    mycursor.execute("""SELECT * FROM diagnostic;""")

    data = mycursor.fetchall()

    # close cursor
    db.close()
	
    return render_template('home.html', data = data)

#about page route
@app.route('/about')
def about():
    return render_template('about.html')

#registration page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        # hash the password that the user ended
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # connect to the database
        db = mysql.connector.connect(host='us-cdbr-iron-east-01.cleardb.net', user='b94531a8a9be0d', password='440412d5', db='heroku_c22f6c727a9c888')

        # set up db cursor
        mycursor = db.cursor()

        # run the query to add the user to the database
        query = f"INSERT INTO Users (userID, userEmail, userPW) VALUES ('{form.username.data}', '{form.email.data}', '{hashed_pw}');"
        mycursor.execute(query)

        # commit the query
        db.commit()

        #close the database
        db.close()

    	# display success message if user successfully registered
        flash(f'Your account has been created. Please login.', 'success')

        # render homepage
        return redirect(url_for('home'))

    # if no validation, render register page
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
