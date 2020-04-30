#this file contains the info needed for user authentication

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
