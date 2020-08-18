# import modules for rendering templates, message display, and url generation
from flask import render_template, url_for, flash, redirect, request, Response

# import wtForm classes for registration and login forms
from project.forms import RegistrationForm, LoginForm, AddForm, UpdateForm, SearchForm, cartForm

# import User model needed for session validation
from project.models import User, Requests, Items, Fulfillments

# import app
from project import app

# import mysql db
from project import get_db

# import bcrypt
from project import bcrypt

# import json
from project import json

# import flask-login
from flask_login import login_user, logout_user, current_user, login_required

# allows printing to console (for debugging)
import sys

############################################################################################
# This is the home page route. It displays the landing page and allows users to            #
# register or login                                                                        #
############################################################################################
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('requests'))

    # render the homepage template, passing data to display
    return render_template('home.html')

############################################################################################
# This is the requests page route. It displays the open requests and has search bar        #
# functionality to display open requests by zip code                                       #
############################################################################################
@app.route('/requests', methods=['GET', 'POST'])
def requests():

    if not current_user.is_authenticated:
        flash(f'You are not yet logged in: Please log in to access the Account page', 'danger')
        return redirect(url_for('login'))

    # set up search bar form object
    form = SearchForm()

    # if zip code form is validly submitted
    if form.validate_on_submit():

        # grab the zip code that was entered
        searchZip = form.searchZip.data

        # display success message if user successfully registered
        flash(f'Returning results for zip code {form.searchZip.data}', 'success')

    # otherwise return any zip code
    else:
        searchZip = ''

    openRequestsObj = Requests()

    requests = openRequestsObj.get_open_requests(searchZip)

    # render the homepage template, passing data to display
    return render_template('requests.html', data = requests, form = form)

#about page route
@app.route('/about')
def about():
    return render_template('about.html')

############################################################################################
# This is the registration page route. Users can register a new account, after which they  #
# are sent to the home page                                                                #
############################################################################################
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
        query = """INSERT INTO Users (userName, userFirstName, userLastName, userStreetAddress, userCity, userState, userZip, userPhoneNumber, userEmail, userPW) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        mycursor.execute(query,(form.username.data, form.firstName.data, form.lastName.data, form.userStreet.data, form.userCity.data, form.userState.data, form.userZip.data, form.userPhone.data, form.email.data, hashed_pw))

        # commit the query
        db.commit()

        mycursor.close()

    	# display success message if user successfully registered
        flash(f'Your account has been created. Please login.', 'success')

        # render account page
        return redirect(url_for('login'))

    # if no data has been submitted, display the registration page
    return render_template('register.html', title='Register', form = form)

############################################################################################
# This is the page for creating new requests.                                              #
############################################################################################
@app.route('/add', methods=['GET', 'POST'])
def add():

    if not current_user.is_authenticated:
        flash(f'You are not yet logged in: Please log in to access the Account page', 'danger')
        return redirect(url_for('login'))

    # create add item form object
    form = AddForm()

    # if add item form is validly submitted
    if form.validate_on_submit():

        # grab the items and quantities that were added to the request
        requestItems = {form.itemsAdded.data}
        requestQuantities = {form.quantitiesAdded.data}

        # convert form result to a comma separated list for processing
        for line in requestItems:
            requestItemsList = line.split (",")

        for line in requestQuantities:
            requestQuantitiesList = line.split (",")

        # create items object
        itemsObj = Items()

        # iterate over the items in the request and verify if they are in the Items table
        for item in requestItemsList:
            inItems = itemsObj.is_in_items(item)
            
            # if item is not in the Items table, add it
            if inItems != True:
                itemsObj.addItem(item)

        # create a new requests object
        requests = Requests()

        # add request to Requests table
        requests.add_request(requestItemsList, requestQuantitiesList, current_user.id, {form.dateRequested.data}, {form.dateNeeded.data}, {form.specialInstructions.data})

        # display success message (this is temporary just to show the form works)
        flash(f'You created a new request!', 'success')

        # redirect to the home page
        return redirect(url_for('home'))

    # if no data has been submitted, display the add item page
    return render_template('add.html', title='Make Your Request', form = form)

############################################################################################
# This is the page for logging useres in, after which they are sent to the home page       #
############################################################################################
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
        query = """SELECT userID, userEmail, userPW from Users WHERE userEmail=%s"""
        mycursor.execute(query, (form.email.data,))
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
                return redirect(next_page) if next_page else redirect(url_for('requests'))

            # if email address is found but password doesn't match, display error message
            else:
                flash('Incorrect password.', 'danger')
        
        # if email address is not found, display error message
        else:
            flash('Email address not found. Have you registered?', 'danger')

    return render_template('login.html', title='Login', form = form)

############################################################################################
# This is the route for the shopping cart (where fulfillments are initiated)               #
############################################################################################
@app.route('/cart', methods=['GET', 'POST'])
def cart():

    # get requests in the user's cart
    cartRequestsObj = Requests()
    requests = cartRequestsObj.get_cart_requests(current_user.id)
    
    if not current_user.is_authenticated:
        flash(f'You are not yet logged in: Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    # set up checkout form (just a checkout button for now)
    form = cartForm()

    # if form is validly submitted
    if form.validate_on_submit():

        # create fulfillment for the requests in the cart
        cartFulfillment = Fulfillments()
        cartFulfillment.create_Fulfillment(current_user.id, requests)

        # display success message 
        flash(f'You have checked out.', 'success')

        # redirect to the home page
        return redirect(url_for('requests'))
    
    # render the carttemplate, passing data to display
    return render_template('cart.html', form = form, data=requests)

############################################################################################
# This is the route for adding a new request to the cart                                   #
############################################################################################
@app.route('/addToCart', methods=['GET', 'POST'])
def addToCart():

    if request.method == 'POST':

        # grab the requestID that was posted
        requestID = request.form['requestID']

        # update the cartID field in the request
        db = get_db()
        mycursor = db.cursor()
        query = """UPDATE requests SET cartID = %s WHERE requestID = %s"""
        mycursor.execute(query, (current_user.id, requestID))
        db.commit()
        mycursor.close()

        # display successmessage to user
        flash(f'The request was added to your cart.', 'success')

    # send the user back to the requests page
    return redirect(url_for('requests'))

############################################################################################
# This is the route for removing a request from a cart                                     #
############################################################################################
@app.route('/removeFromCart', methods=['GET', 'POST'])
def removeFromCart():

    if request.method == 'POST':

        # grab the requestID that was posted
        requestID = request.form['requestID']

        # update the cartID field in the request
        db = get_db()
        mycursor = db.cursor()
        query = """UPDATE requests SET cartID = NULL WHERE requestID = %s"""
        mycursor.execute(query, (requestID,))
        db.commit()
        mycursor.close()

        # display successmessage to user
        flash(f'The request was removed from your cart.', 'success')

    # send the user back to the requests page
    return redirect(url_for('cart'))

############################################################################################
# This is the route for logging out of the app                                             #
############################################################################################
@app.route('/logout')
def logout():

    # end the session for the user
    logout_user()

    # display message to user
    flash(f'You have been logged out.', 'success')

    # send the user back to the homepage
    return redirect(url_for('home'))

# this route is only used by the autocomplete search bar on the add.html page
@app.route('/_autocomplete', methods=['GET'])
def autocomplete():

    # create an Items object and get a list of all the items
    itemsObj = Items()
    items = itemsObj.get_items()

    # convert list to json format (required per Bootstrap Autocomplete) and respond to request
    return Response(json.dumps(items), mimetype='application/json')

# user account info
@app.route('/account', methods=['GET', 'POST'])
def account():

    # if user is not already logged in, send them to the registration page
    if not current_user.is_authenticated:
        flash(f'You are not yet logged in: Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    #get acct info from server
    db = get_db()

    # set up db cursor
    mycursor = db.cursor()

    # run the query to add the user to the database
    query = f"SELECT userName, userFirstName, userLastName, userStreetAddress, userCity, userState, userZip, userPhoneNumber, userEmail FROM Users WHERE userId = '{current_user.id}';"
    mycursor.execute(query)
    userTuple = mycursor.fetchall()
    for u in userTuple:
        userInfo = {'userName': u[0], 'userFirstName': u[1], 'userLastName': u[2], 'userStreetAddress': u[3], 'userCity': u[4], 'userState': u[5], 'userZip': u[6], 'userPhoneNumber': u[7], 'userEmail': u[8]}
    mycursor.close()
    
    # get data from server for requests by userId of logged in user
    #get requestID, needByDate, requestDate, fulfilled, count
    #with count = number of items associated with request
    db = get_db()
    # set up db cursor
    mycursor = db.cursor()
    query = f"SELECT requestID, requestDate, needByDate, COUNT(*), fID FROM Requests JOIN requestedItems ON Requests.requestID = RequestedItems.rID WHERE uID ='{current_user.id}' GROUP BY requestID;"
    mycursor.execute(query)
    requestTuple = mycursor.fetchall()
    requests = []
    for r in requestTuple:
        if r[4] == None:
            fulfilled = False
        else:
            fulfilled = True

        requests.append({'requestID': r[0], 'requestDate': r[1], 'needByDate': r[2], 'count': r[3], 'fulfilled': fulfilled})
    mycursor.close()


    # get data from server for requests fulfilled by userId of logged in user
    #select RequestID, user first name, user last name, user phone, needByDate, fulfillmentDate
    db = get_db()
    # set up db cursor
    mycursor = db.cursor()

    query = f"SELECT fulfillmentID, transactionDate FROM Fulfillments WHERE uID ='{current_user.id}';"
    mycursor.execute(query)
    fulfillTuple = mycursor.fetchall()
    fulfillments = []

    for f in fulfillTuple:
        fulfillments.append({'fulfillmentID': f[0], 'transactionDate': f[1]})
   
    mycursor.close()

    return render_template('account.html', title='Account', userInfo=userInfo, requests=requests, fulfillments=fulfillments)

#update user information page route
@app.route('/updateUser', methods=['GET', 'POST'])
def updateUser():

    # if user is not already logged in, send them to the login page
    if not current_user.is_authenticated:
        flash(f'You are not yet logged in: Please log in to update your information', 'danger')
        return redirect(url_for('login'))

    # create registration form object
    form = UpdateForm()

    # if registration form has been validly submitted
    if form.validate_on_submit():


        # hash the password that the user ended
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        db = get_db()

        # set up db cursor
        mycursor = db.cursor()

        # run the query to update the info in the database
        query = """UPDATE Users SET userFirstName = %s, userLastName = %s, userStreetAddress = %s, userCity = %s, userState = %s, userZip = %s, userPhoneNumber = %s, userPW = %s WHERE userID = %s;"""
        mycursor.execute(query, (form.firstName.data, form.lastName.data, form.userStreet.data, form.userCity.data, form.userState.data, form.userZip.data, form.userPhone.data, hashed_pw, current_user.id))
        db.commit()
        mycursor.close()

        # display success message if user successfully registered
        flash(f'Thank you for updating your information!', 'success')

        # render account page
        return redirect(url_for('account'))

    # get current logged in user info to prepopulate form on update page
    db = get_db()
    mycursor = db.cursor()
    query = f"SELECT userFirstName, userLastName, userStreetAddress, userCity, userState, userZip, userPhoneNumber FROM Users WHERE userID = '{current_user.id}';"
    mycursor.execute(query)
    userDataTuple = mycursor.fetchall()
    #place data from tuple into form
    for d in userDataTuple:
        form.firstName.data = d[0]
        form.lastName.data = d[1]
        form.userStreet.data = d[2]
        form.userCity.data = d[3]
        form.userState.data = d[4]
        form.userZip.data = d[5]
        form.userPhone.data = d[6]


    # if no data has been submitted, display the registration page
    return render_template('updateUser.html', title='Update User Information', form = form)

#Request display page route
@app.route('/displayRequest', methods=['GET', 'POST'])
def displayRequest():
    if request.method == 'POST':
        ##SQL for deleting request
        db = get_db()

        # set up db cursor
        mycursor = db.cursor()

        # run the query to delete the info in the database
        query = f"DELETE FROM RequestedItems WHERE rID = '{request.form.get('requestID')}';"
        mycursor.execute(query)
        db.commit()
        mycursor.close()

        db = get_db()

        # set up db cursor
        mycursor = db.cursor()

        # run the query to delete the info in the database
        query = f"DELETE FROM Requests WHERE requestID = '{request.form.get('requestID')}';"
        mycursor.execute(query)
        db.commit()
        mycursor.close()

        flash(f'Request Deleted', 'success')
        return redirect(url_for('account'))

    ##USE REQUEST ID TO MAKE QUERY
    ##query DB here to get all item names and item quantities assoc with that req
    db = get_db()
    # set up db cursor
    mycursor = db.cursor()
    query = f"SELECT Items.itemName, RequestedItems.quantity FROM RequestedItems JOIN Items ON RequestedItems.iID = Items.itemID WHERE RequestedItems.rID = '{request.args.get('requestID')}';"
    mycursor.execute(query)
    itemTuple = mycursor.fetchall()
    items = []
    for i in itemTuple:
        items.append({'itemName': i[0], 'quantity': i[1]})
    mycursor.close()

    ##USE REQUEST ID TO MAKE QUERY
    ##query DB here to get all request info associated with that request ID
    db = get_db()
    # set up db cursor
    mycursor = db.cursor()
    query = f"SELECT requestID, requestDate, needByDate, specialInstructions FROM Requests WHERE requestID ='{request.args.get('requestID')}';"
    mycursor.execute(query)
    requestDataTuple = mycursor.fetchall()
    requestData = {}
    for d in requestDataTuple:
        requestData = {'requestID': d[0], 'requestDate': d[1], 'needByDate': d[2], 'instructions': d[3]}
    mycursor.close()

    return render_template('displayRequest.html', title='Your Request', items=items, requestData=requestData)

#Fulfillment display page route
@app.route('/displayFulfillment', methods=['GET', 'POST'])
def displayFulfillment():

    if request.method == 'POST':
        ##SQL for deleting request
        db = get_db()

        # set up db cursor
        mycursor = db.cursor()

        # run the query to update the info in the database
        query = f"UPDATE Requests SET fID = NULL WHERE fID = '{request.form.get('fulfillmentID')}';"
        mycursor.execute(query)
        db.commit()
        mycursor.close()

        db = get_db()

        # set up db cursor
        mycursor = db.cursor()

        # run the query to delete the info in the database
        query = f"DELETE FROM Fulfillments WHERE fulfillmentID = '{request.form.get('fulfillmentID')}';"
        mycursor.execute(query)
        db.commit()
        mycursor.close()
        ##put sql query here to delete request by fulfillmentID
        flash(f'Fulfillment Deleted', 'success')
        return redirect(url_for('account'))

    ##USE FULFILLMENT ID TO MAKE QUERY
    ##query DB here to get all fulfillment data
    db = get_db()
    # set up db cursor
    mycursor = db.cursor()

    query = f"SELECT fulfillmentID, transactionDate FROM Fulfillments WHERE fulfillmentID ='{request.args.get('fulfillmentID')}';"
    mycursor.execute(query)
    fulfillTuple = mycursor.fetchall()
    fulfillmentData = {}

    for f in fulfillTuple:
        fulfillmentData = {'fulfillmentID': f[0], 'fulfillDate': f[1]}
   
    mycursor.close()

    #second query that gives all request and assoc user info for each request fulfilled on that fulfillment
    db = get_db()
    # set up db cursor
    mycursor = db.cursor()

    requestData = []
    #query for request info with associated user data for  the user who made that request
    query = f"SELECT Requests.requestID, Users.userFirstName, Users.userLastName, Users.userStreetAddress, Users.userCity, Users.userState, Users.userZip, Users.userPhoneNumber, Users.userEmail, Requests.needByDate, Requests.specialInstructions FROM Requests JOIN Users ON Requests.uID = Users.userID WHERE Requests.fID ='{request.args.get('fulfillmentID')}';"
    mycursor.execute(query)
    requestDetailsTuple = mycursor.fetchall()
    mycursor.close()
    for d in requestDetailsTuple:
        details = []
        itemDeets = []
        combined = []
        details.append({'requestID': d[0], 'firstName': d[1], 'lastName': d[2], 'userStreet': d[3], 'userCity': d[4], 'userState': d[5], 'userZip': d[6], 'userPhone': d[7], 'userEmail': d[8], 'needByDate': d[9], 'specialInstructions': d[10]});
        db = get_db()
        mycursor = db.cursor()
        #for each request, query for item info on all items within that request
        query = f"SELECT Items.itemName, RequestedItems.quantity FROM RequestedItems JOIN Items ON RequestedItems.iID = Items.itemID WHERE RequestedItems.rID = '{d[0]}';"
        mycursor.execute(query)
        itemDetailsTuple = mycursor.fetchall()
        mycursor.close()
        for i in itemDetailsTuple:
            itemDeets.append({'itemName': i[0], 'quantity': i[1]})

        combined.append(details)
        combined.append(itemDeets)
        requestData.append(combined)
   
    return render_template('displayFulfillment.html', title='Your Request', fulfillmentData=fulfillmentData, requestData=requestData)