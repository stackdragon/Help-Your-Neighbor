# import modules for rendering templates, message display, and url generation
from flask import render_template, url_for, flash, redirect, request

# import wtForm classes for registration and login forms
from project.forms import RegistrationForm, LoginForm, AddForm, UpdateForm

# import User model needed for session validation
from project.models import User

# import app
from project import app

# import mysql db
from project import get_db

# import bcrypt
from project import bcrypt

# import flask-login
from flask_login import login_user, logout_user, current_user, login_required

# dummy data for project submission step 3
requests = [
    {
        'city': 'San Francisco',
        'zip': '94016',
        'userName': 'Bob437',
        'item1': 'Toilet paper',
        'qty1': 4,
        'needByDate': 'May 9, 2020',
        'specialInstructions': 'Please leave on back porch steps.'
    },

    {
        'city': 'San Francisco',
        'zip': '94118',
        'userName': 'catlady',
        'item1': 'Cat food',
        'qty1': 1,
        'needByDate': 'May 8, 2020',
        'specialInstructions': 'Precious only eats Fancy Feast.'
    },
    {
        'city': 'Oakland',
        'zip': '94604',
        'userName': 'PlantLuvr',
        'item1': 'Tofu',
        'qty1': 5,
        'needByDate': 'May 12, 2020',
        'specialInstructions': 'Organic please.'
    }
    ]

#home page route
@app.route('/')
@app.route('/home')
def home():
    
    db = get_db()

    # set up db cursor
    mycursor = db.cursor()

    # the query to get and display all of the open requests needs to go here
    # mycursor.execute("""SELECT userID, userName, userEmail FROM Users;""")
    # requests = mycursor.fetchall()

    mycursor.close()
	
    # render the homepage template, passing data to display
    return render_template('home.html', data = requests)

#about page route
@app.route('/about')
def about():
    return render_template('about.html')

#registration page route
@app.route('/register', methods=['GET', 'POST'])
def register():

    # if user is already logged in, send them to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    # create registration form object
    form = RegistrationForm()

    # if registration form has been validly submitted
    if form.validate_on_submit():

        # hash the password that the user ended
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        db = get_db()

        # set up db cursor
        mycursor = db.cursor()

        # run the query to add the user to the database
        query = f"INSERT INTO Users (userName, userEmail, userPW) VALUES ('{form.username.data}', '{form.email.data}', '{hashed_pw}');"
        mycursor.execute(query)

        # commit the query
        db.commit()

        mycursor.close()

    	# display success message if user successfully registered
        flash(f'Your account has been created. Please login.', 'success')

        # render account page
        return redirect(url_for('login'))

    # if no data has been submitted, display the registration page
    return render_template('register.html', title='Register', form = form)

#add page route
@app.route('/add', methods=['GET', 'POST'])
def add():

    # create add item form object
    form = AddForm()

    # if add itme form is validly submitted
    if form.validate_on_submit():

        # query db and add request here

        # display success message (this is temporary just to show the form works)
        flash(f'You created a new request!', 'success')

        # redirect to the home page
        return redirect(url_for('home'))

    # if no data has been submitted, display the add item page
    return render_template('add.html', title='Make Your Request', form = form)

# login page route
@app.route('/login', methods=['GET', 'POST'])
def login():

    # if user is already logged in, send them to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    # create login form object
    form = LoginForm()

    # if login form has been validly submitted
    if form.validate_on_submit():

        db = get_db()
        # set up db cursor
        mycursor = db.cursor()

        # query the Users mySQL table for the userID, email address and password
        query = f"SELECT userID, userEmail, userPW from Users WHERE userEmail='{form.email.data}';"
        mycursor.execute(query)
        user = mycursor.fetchone()
        mycursor.close()

        # if the user exists, store the info provided by the query in separate variables
        if user:
            userID= user[0]
            email = user[1]
            password = user[2]

            # then verify that the entered password matches the password stored in the db
            if user and bcrypt.check_password_hash(password, form.password.data):

                # if so, create the a user object (this is necessary for Flask-Login)
                user = User(userID, email, password)

                # call Flask-Login login_user function to create the session for the user
                login_user(user, remember=form.remember.data)

                # if there is a next parameter in the url, grab it to forward the user to the appropriate name.
                next_page = request.args.get('next')

                # now that the user has logged in, send her to either the next page or the account page
                return redirect(next_page) if next_page else redirect(url_for('account'))

            # if email address is found but password doesn't match, display error message
            else:
                flash('Incorrect password.', 'danger')
        
        # if email address is not found, display error message
        else:
            flash('Email address not found. Have you registered?', 'danger')

    return render_template('login.html', title='Login', form = form)

# logout page route
@app.route('/logout')
def logout():

    # end the session for the user
    logout_user()

    # display message to user
    flash(f'You have been logged out.', 'success')

    # send the user back to the homepage
    return redirect(url_for('home'))

# user account info
@app.route('/account', methods=['GET', 'POST'])
def account():

    # if user is not already logged in, send them to the registration page
    #if not current_user.is_authenticated:
    #    return redirect(url_for('register'))

    # create registration form object
    form = UpdateForm()

    # if registration form has been validly submitted
    if form.validate_on_submit():

        # hash the password that the user ended
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        db = get_db()

        # set up db cursor
        mycursor = db.cursor()

        # run the query to add the user to the database
        #PUT UPDATE QUERY HERE!

        #query = f"INSERT INTO Users (userName, userEmail, userPW) VALUES ('{form.username.data}', '{form.email.data}', '{hashed_pw}');"
        #mycursor.execute(query)

        # commit the query
        #db.commit()

        mycursor.close()

        # display success message if user successfully registered
        flash(f'Your account has been updated', 'success')

        # render homepage
        return redirect(url_for('account'))

    #get acct info from server
    #sham data as a placeholder
    userInfo = {'username': 'enigMAN', 'firstName': 'Alan', 'lastName': 'Turing', 'userStreet': 'Hampton Road', 'userCity': 'Teddington', 'userState': 'EN', 'userZip': 'TW110', 'userPhone': '360-555-5555', 'userEmail': 'aturing@oregonstate.edu'}
    
    # get data from server for requests by userId of logged in user
    #get requestID, needByDate, requestDate, fulfilled, count
    #with count = number of items associated with request
    #sorted by fulfilled no to fulfilled yes and then date requested newest to oldest (OR MAYBE NEED BY OLDEST TO NEWEST?)
    #sham data as a placeholder for now
    requests = [
        {'requestID': 12, 'needByDate': 'April 19, 2020', 'requestDate': 'April 17, 2020', 'fulfilled': False, 'count': 2},
        {'requestID': 15, 'needByDate': 'April 29, 2020', 'requestDate': 'April 23, 2020', 'fulfilled': False, 'count': 5},
        {'requestID': 11, 'needByDate': 'April 2, 2020', 'requestDate': 'March 25, 2020', 'fulfilled': True, 'count': 1}
        ]

    # get data from server for requests fulfilled by userId of logged in user
    #select RequestID, user first name, user last name, user phone, needByDate, fulfillmentDate
    #sorted by date fulfilled newest to oldest
    #sham data as a placeholder for now
    fulfillments = [
        {'fulfillmentID': 10, 'fulfillDate': 'March 24, 2020'},
        {'fulfillmentID': 8, 'fulfillDate': 'February 25, 2020'}
        ]

    return render_template('account.html', form=form, title='Account', userInfo=userInfo, requests=requests, fulfillments=fulfillments)

