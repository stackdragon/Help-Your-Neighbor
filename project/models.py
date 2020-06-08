#this file contains the info needed for user authentication and other db helper functions

from project import login_manager, get_db
from project.forms import date, datetime
import time
from flask_login import UserMixin

############################################################################################
# custom class for working with Fulfillments data                                          #
# Methods:																																								 #
#   create_Fulfillment(userID, requests): Generates a fulfillment for the requests in the  #
#                       									user's cart 																		 #
############################################################################################
class Fulfillments():

	def create_Fulfillment(self, userID, requests):

		self.userID = userID
		self.requests = requests

		db = get_db()
		mycursor = db.cursor()
		query = """INSERT INTO Fulfillments (uid, transactionDate, transactionTime) VALUES (%s, CURDATE(), CURTIME())"""
		mycursor.execute(query, (userID,))
		db.commit()
		mycursor.close()

		# get id for fulfillment that was just added, since this is needed as a foreign key
		mycursor = db.cursor()
		query = f"""SELECT LAST_INSERT_ID();"""
		mycursor.execute(query)
		fulfillmentID = mycursor.fetchone()
		mycursor.close()

		# update the fulfillmentID for all of the requests
		for request in requests:
			# add the foreign key to the Requests table
			mycursor = db.cursor()
			query = """UPDATE requests SET fID = %s WHERE requestID = %s"""
			mycursor.execute(query, (fulfillmentID[0], request))
			db.commit()
			mycursor.close()

			# remove the request from the user's cart
			mycursor = db.cursor()
			query = """UPDATE requests SET cartID = NULL WHERE requestID = %s"""
			mycursor.execute(query, (request,))
			db.commit()
			mycursor.close()

############################################################################################
# custom class for working with Items data                                                 #
# Methods:																																								 #
#   getItems(): returns a list of all items in the Items table                             #
#   is_in_items(itemname): returns True if item name is included in Items table,           #
#                          False if not                                                    #
#   addItem(itemName): adds ann item with the passed name to the Items table               #
############################################################################################
class Items():
		# on initialization, get all open requests
	def __init__(self):

		# set up db cursor
		db = get_db()
		mycursor = db.cursor()

		# grab all items in the db
		query = f"""SELECT itemName FROM items;"""

		mycursor.execute(query)

		# convert mysql result (which is in tuple) to be in a standard list
		# because jquery autocomplete requires data to be in list format
		self.itemsData = [item[0] for item in mycursor.fetchall()]
		mycursor.close()

	def get_items(self):

		# return a list of all items
		return self.itemsData

	def is_in_items(self, itemName):

		# check to see if a given item is in the Items table
		db = get_db()
		mycursor = db.cursor()

		query = """SELECT itemName FROM Items WHERE itemName= %s"""
		mycursor.execute(query, (itemName,))
		self.result = mycursor.fetchall()
		mycursor.close()

		# if query result is not null, item is in the table
		if self.result:
			return True

		else:
			return False

	def addItem(self, itemName):

		# check to see if a given item is in the Items table
		db = get_db()
		mycursor = db.cursor()

		query = """INSERT INTO Items (itemName) VALUES (%s)"""
		mycursor.execute(query, (itemName,))

		# commit the query
		db.commit()
		mycursor.close()


############################################################################################
# class for working with requests                                                          #
# Methods:																																								 #
#   getOpenRequests(): returns a dictionary of all open requests by zip code               #
#   add_request(items, quantities, userID, requestDate, needByDate, specialInstructions):  #
#       adds a request to the db                                                           #
#   add_to_cart(userID, requestID): adds a request to the user's cart     								 #     
#		get_cart_requests(userID): get requests in a cart for a specific user                  #
############################################################################################
class Requests():

	def get_open_requests(self, searchZip):

		# grab the zip code that was passed as an argument
		self.searchZip = searchZip

		# create a new dictionary to store all of the open requests
		self.openRequestsDict = {};

		# set up db cursor
		db = get_db()
		mycursor = db.cursor()

		# run query to grab open requets
		query = f"""SELECT r.requestID, u.userName, u.userCity, u.userState, u.userZip, r.needByDate, r.specialInstructions, i.itemID, i.itemname, ri.quantity, r.cartID
								FROM users u
								INNER JOIN requests r ON u.userID = r.uID
								INNER JOIN requestedItems ri ON r.requestID = ri.rID
								INNER JOIN items i ON ri.iID = i.itemID
								WHERE r.fID IS NULL { self.searchZip } AND r.cartID IS NULL
								ORDER BY r.requestID ASC;"""

		mycursor.execute(query)
		requestsData = mycursor.fetchall()
		mycursor.close()

		# if any open requests are returned from the query
		if requestsData:

			# iterate over the open requets
			for row in requestsData:

				# if the requestID already exists in openrRequestsDict
				if row[0] in self.openRequestsDict.keys(): 

					# create a new dictionary to store information about the additional item in the request
					invDict = {'itemID': row[7], 'itemName': row[8], 'quantity': row[9]}

					# append the new dictionary to the list of items already associated with that requestID
					self.openRequestsDict[row[0]]['items'].append(invDict)

				# if the requestID doesn't already exist in openRequestsDict 
				else:

					# this list will hold all of the items associated with the request
					items = []

					# create a new dictionary to store each element of this requestID
					rowDict = {'userName': row[1], 'userCity': row[2], 'userState': row[3], 'userZip': row[4], 'needByDate': row[5], 'specialInstructions': row[6], 'items': items}

					# create a new dictionary to store information about the first item associated with this requestID
					invDict = {'itemID': row[7], 'itemName': row[8], 'quantity': row[9]}

					# append the dictionary of items to the items list in rowDict
					items.append(invDict);

					# associate the items list with rowDict
					rowDict.update({'items': items})

					# add rowDict to the requests dictionary using requestsID as the key
					self.openRequestsDict[row[0]] = rowDict

		# return the dictionary of all open requests
		return self.openRequestsDict

	def get_cart_requests(self, userID):

		# grab the zip code that was passed as an argument
		self.userID = userID

		# create a new dictionary to store all of the open requests
		self.cartRequestsDict = {};

		# set up db cursor
		db = get_db()
		mycursor = db.cursor()

		# run query to grab open requets
		query = f"""SELECT r.requestID, u.userName, u.userCity, u.userState, u.userZip, r.needByDate, r.specialInstructions, i.itemID, i.itemname, ri.quantity, r.cartID
								FROM users u
								INNER JOIN requests r ON u.userID = r.uID
								INNER JOIN requestedItems ri ON r.requestID = ri.rID
								INNER JOIN items i ON ri.iID = i.itemID
								WHERE r.fID IS NULL AND r.cartID = {self.userID}
								ORDER BY r.requestID ASC;"""

		mycursor.execute(query)
		requestsData = mycursor.fetchall()
		mycursor.close()

		# if any open requests are returned from the query
		if requestsData:

			# iterate over the open requets
			for row in requestsData:

				# if the requestID already exists in openrRequestsDict
				if row[0] in self.cartRequestsDict.keys(): 

					# create a new dictionary to store information about the additional item in the request
					invDict = {'itemID': row[7], 'itemName': row[8], 'quantity': row[9]}

					# append the new dictionary to the list of items already associated with that requestID
					self.cartRequestsDict[row[0]]['items'].append(invDict)

				# if the requestID doesn't already exist in openRequestsDict 
				else:

					# this list will hold all of the items associated with the request
					items = []

					# create a new dictionary to store each element of this requestID
					rowDict = {'userName': row[1], 'userCity': row[2], 'userState': row[3], 'userZip': row[4], 'needByDate': row[5], 'specialInstructions': row[6], 'items': items}

					# create a new dictionary to store information about the first item associated with this requestID
					invDict = {'itemID': row[7], 'itemName': row[8], 'quantity': row[9]}

					# append the dictionary of items to the items list in rowDict
					items.append(invDict);

					# associate the items list with rowDict
					rowDict.update({'items': items})

					# add rowDict to the requests dictionary using requestsID as the key
					self.cartRequestsDict[row[0]] = rowDict

		# return the dictionary of all open requests
		return self.cartRequestsDict

	def add_request(self, items, quantities, userID, requestDate, needByDate, specialInstructions):

		# add request to the Request table
		db = get_db()
		mycursor = db.cursor()
		query = """INSERT INTO Requests(requestDate, needByDate, specialInstructions, uID) VALUES (%s, %s, %s, %s)""" 
		mycursor.execute(query, (requestDate.pop(), needByDate.pop(), specialInstructions.pop(), userID ))
		db.commit()
		mycursor.close()

		# get id for request that was just added, since this is needed as a foreign key
		mycursor = db.cursor()
		query = f"""SELECT LAST_INSERT_ID();"""
		mycursor.execute(query)
		requestID = mycursor.fetchone()
		mycursor.close()

		# iterate over list of item names that was passed as an argument
		itemListLength = len(items)
		for i in range(itemListLength):

			#grab itemID associated with that item name from the Items table
			mycursor = db.cursor()
			query = """SELECT itemID FROM Items WHERE itemName = %s"""
			mycursor.execute(query, (items[i],))
			itemID = mycursor.fetchone()
			mycursor.close()

			#insert item id, requestid, and quantity into requestedItems table
			mycursor = db.cursor()
			query = """INSERT INTO requestedItems (iID, rID, quantity) VALUES (%s, %s, %s)"""
			mycursor.execute(query, (itemID[0], requestID[0], quantities[i]))
			db.commit()
			mycursor.close()

############################################################################################
# this is the User class required by Flask-login                                           #
############################################################################################
class User(UserMixin):
	def __init__(self, id, email, password):
		self.id = id
		self.email = email
		self.password = password

############################################################################################
# this is the login manager class required by Flask-login                                  #
############################################################################################
@login_manager.user_loader
def load_user(user_id):

	# set up db cursor
	db = get_db()
	mycursor = db.cursor()

	# see if the user email exists in the db. grab email address and password
	query = f"SELECT userID, userEmail, userPW from Users WHERE userID=%s;"
	mycursor.execute(query,(user_id,))
	user = mycursor.fetchone()
	mycursor.close()

	if user: 
		# grab the email address and password from the query
		id = user[0]
		email = user[1]
		password = user[2]

		# create new user object
		userObj = User(id, email, password)
		return userObj

	# if user is not found, return none
	return user
