# Help Your Neighbor App

It can often be difficult for those who are elderly, disabled, and otherwise homebound to perform tasks such as grocery shopping or picking up medication. This webapp seeks to help address this problem by providing an interface to facilitate neighborhood acts of kindness by connecting recipients of aid to those who are able to provide it.

Recipients can log on to the website to place request posts for needed items. Donors can log on and search the requests to assess what they can help with, and then assign themselves to fulfill those requests. This database-driven website records user information, the requests for items that are needed, as well as a record of all matched donor/recipient transactions.

## Usage

Visit [https://helpyourneighbor.herokuapp.com/](https://helpyourneighbord.herokuapp.com/)

To login, use the following username and password or register your own:
username: test@test.com
password: test

## Features

**Create your own account to start initiating and fulfilling requests**

![Screenshot add items page](/project_images/1-1.png)

**Search user requests for needed items globally or within your local zip code**

![Screenshot of requests page](/project_images/3-1.png)

**Add your own requests for needed goods**

![Screenshot add items page](/project_images/2-1.png)

## Built with

-[Flask](https://flask.palletsprojects.com/en/1.1.x/)
Backend framework

-[Bootstrap](https://getbootstrap.com/docs/4.1/getting-started/introduction/)
Front-end CSS framework

-[Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/en/latest/)
Password hashing

-[Flask-Login](https://flask-login.readthedocs.io/en/latest/)
User login / session management

-[Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/)
Form validation and rendering

-[Heroku](https://www.heroku.com)
Hosting

-[MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)
MySQL server communication

## Setting up a development environment

Clone the source locally

```
$ git clone https://github.com/steveperreaul/helpyourneighbor
$ cd helpyourneighbor
```

Create a new virtual environment inside the directory

```
$ python3 -m venv env
```

Activate the virtual environment

```
$ source env/bin/activate
```

Install the required packages

```
(env) $ pip install -r requirements.txt
```

Launch the app locally

```
(env) $ python3 run.py
```

Once the webserver has been activated, the app can be viewed by visiting `http://localhost:5000`.

Note this app requires Python version 3.6 or later. You can check your version with the command `python3 -v`.
<br>Update to the latest version using `sudo apt-get install python3.7`.
