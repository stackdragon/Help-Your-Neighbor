#this file contains the info needed for user authentication and other db helper functions

from project import login_manager, get_db
from flask_login import UserMixin

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

		query = f"""select itemName from Items where itemName='{itemName}';"""
		mycursor.execute(query)
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

		query = f"""INSERT INTO Items (itemName) VALUES ('{itemName}');"""
		mycursor.execute(query)

		# commit the query
		db.commit()
		mycursor.close()


############################################################################################
# class for working with requests                                                          #
# Methods:																																								 #
#   getOpenRequests(): returns a dictionary of all open requests                           #
#   add_request(items, quantities, userID, requestDate, needByDate, specialInstructions):  #
#       adds a request to the db                                                           #
############################################################################################
class Requests():

	# on initialization, get all open requests
	def __init__(self, searchZip):

		# grab the zip code that was passed as an argument
		self.searchZip = searchZip

		# create a new dictionary to store all of the open requests
		self.openRequestsDict = {};

		# set up db cursor
		db = get_db()
		mycursor = db.cursor()

		# see if the user email exists in the db. grab email address and password
		query = f"""SELECT r.requestID, u.userName, u.userCity, u.userState, u.userZip, r.needByDate, r.specialInstructions, i.itemID, i.itemname, ri.quantity
								FROM users u
								INNER JOIN requests r ON u.userID = r.uID
								INNER JOIN requestedItems ri ON r.requestID = ri.rID
								INNER JOIN items i ON ri.iID = i.itemID
								WHERE r.fID IS NULL { self.searchZip }
								ORDER BY r.requestID ASC;"""

		mycursor.execute(query)
		requestsData = mycursor.fetchall()
		mycursor.close()

		# if any requests exist
		if requestsData:

			for row in requestsData:

				# if the requestID already exists in openrRequestsDict
				if row[0] in self.openRequestsDict.keys(): 

					# create a new dictionary to store information about the additional item in the request
					invDict = {'itemID': row[7], 'itemName': row[8], 'quantity': row[9]}

					# append the new dictionary to the list of items associated with that requestID
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

	def get_open_requests(self):

		# return the dictionary of all open requests
		return self.openRequestsDict

	def add_request(self, items, quantities, userID, requestDate, needByDate, specialInstructions):

		db = get_db()
		mycursor = db.cursor()

		# build queries to add request to database tables
		query = f"INSERT INTO Requests(requestDate, needByDate, specialInstructions, uID) VALUES ('{ requestDate.pop() }', '{ needByDate.pop() }', '{ specialInstructions.pop() }', { userID });"""
		mycursor.execute(query)
		db.commit()
		mycursor.close()

		# get id for request that was just added
		mycursor = db.cursor()
		query = f"""SELECT LAST_INSERT_ID();"""
		mycursor.execute(query)
		requestID = mycursor.fetchone()
		mycursor.close()

		# iterate over items list
		itemListLength = len(items)

		for i in range(itemListLength):

			#grab item id
			mycursor = db.cursor()
			query = f"""SELECT itemID from Items WHERE itemName = '{ items[i] }';"""
			mycursor.execute(query)
			itemID = mycursor.fetchone()
			mycursor.close()

			#insert item id, requestid, and quantity into requestedItems table
			mycursor = db.cursor()
			query = f"""INSERT INTO requestedItems (iID, rID, quantity) VALUES ({ itemID[0] }, { requestID[0] }, { quantities[i] });"""
			mycursor.execute(query)
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
# required per Flask-login
@login_manager.user_loader
def load_user(user_id):

	# set up db cursor
	db = get_db()
	mycursor = db.cursor()

	# see if the user email exists in the db. grab email address and password
	query = f"SELECT userID, userEmail, userPW from Users WHERE userID='{user_id}';"
	mycursor.execute(query)
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
