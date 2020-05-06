#this file contains the info needed for user authentication and other db helper functions

from project import login_manager, get_db
from flask_login import UserMixin

# this is the User class required by Flask-login
class User(UserMixin):
	def __init__(self, id, email, password):
		self.id = id
		self.email = email
		self.password = password

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



# class will retrieve all requests from MySQL db and has handy methods for working with requests data
class Requests():

	# on initialization, get all open requests
	def __init__(self):

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
								WHERE r.fID IS NULL
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
