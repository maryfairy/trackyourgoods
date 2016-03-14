### Udacity FSWD Project 3
### Track your goods, a way to calculate value of your 
### household good for renter's insurance.

### Import the libraries used for Closet Item Project
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Closet, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import os
import shutil
from flask import make_response
import requests
# CSRF Documentation:
# https://media.readthedocs.org/pdf/flask-seasurf/latest/flask-seasurf.pdf
'''
Corresponding code will need to be added to the templates where POST, PUT, and DELETE HTTP
'''
from flask.ext.seasurf import SeaSurf


app = Flask(__name__)
csrf = SeaSurf(app)
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

## added in client_secrets.json file from console.google...
CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Track Your Goods"

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Connect to Database and create database session
engine = create_engine('sqlite:///trackyourgoods.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

### AUTH Code(all copied from the lesson)
# Create anti-forgery state token
@csrf.exempt
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
					for x in xrange(32))
	login_session['state'] = state
	# prevents CSRF attacks at logn
	#return "The current session state is %s" % login_session['state']
	return render_template('login.html', STATE=state)

@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# see if user exists, if it doesn't make a new one
	user_id = getUserID(data["email"])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

# User Helper Functions


def createUser(login_session):
	newUser = User(name=login_session['username'], email=login_session[
				   'email'], picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id

def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user

def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
		# Only disconnect a connected user.
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(
			json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = credentials.access_token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		# Reset the user's sesson.
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']

		# Change logout so you remain on homepage closets/
		#response = make_response(json.dumps('Successfully disconnected.'), 200)
		#response.headers['Content-Type'] = 'application/json'
		
		response = "<script>function myFunction() {alert('Successfully disconnected.');}</script><body onload='myFunction()''>"
		return response
	else:
		# For whatever reason, the given token was invalid.
		response = make_response(
			json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response

# JSON APIs to view Closet Information
@app.route('/closet/<int:closet_id>/item/JSON')
def closetItemJSON(closet_id):
    closet = session.query(Closet).filter_by(id=closet_id).one()
    items = session.query(Item).filter_by(
        closet_id=closet_id).all()
    return jsonify(Item=[i.serialize for i in items])


@app.route('/closet/<int:closet_id>/item/<int:item_id>/JSON')
def itemItemJSON(closet_id, item_id):
    Items = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=Items.serialize)

### JSON APIs (basically same format as in the closet lesson)
@app.route('/closet/<int:closet_id>/item/JSON')
def closetMenuJSON(closet_id):
	closet = session.query(Closet).filter_by(id=closet_id).one()
	items = session.query(Item).filter_by(
		closet_id=closet_id).all()
	return jsonify(Items=[i.serialize for i in items])

@app.route('/closet/<int:closet_id>/item/<int:item_id>/JSON')
def ItemJSON(closet_id, item_id):
	Item = session.query(Item).filter_by(id=item_id).one()
	return jsonify(Item=Item.serialize)

@app.route('/closet/JSON')
def closetsJSON():
	closets = session.query(Closet).all()
	return jsonify(closets=[r.serialize for r in closets])

@app.route('/closet/<int:closet_id>/item/<int:item_id>/JSON')
def ItemJSON(closet_id, item_id):
	items = session.query(Item).filter_by(id=item_id).one()
	return jsonify(Item=items.serialize)

## Part 1: Add in all Mock/Ups / URLs

# Show all Closets
@app.route('/')
@app.route('/closets/')
def showClosets():
	credentials = login_session.get('credentials')
	if credentials is None:
		##TODO: make alert function and then redirect to Login Page
		return redirect('/login')
		#response = "<script>function myFunction() {alert('Not Loggedin, Please Login.'); }</script><body onload='myFunction()''>"
	currentUserId = login_session['user_id']
	closets = session.query(Closet).filter_by(user_id = currentUserId).order_by(asc(Closet.name))
	## Only want to make the users closets visible
	if 'username' not in login_session:
		return render_template('publicclosets.html', closets=closets, login_session=login_session)
	else:
		return render_template('closets.html', closets=closets, login_session=login_session)

# CREATE a new Closet
@app.route('/closets/new/', methods=['GET', 'POST'])
def newCloset():
	if request.method == 'POST':
		newCloset = Closet(
			name=request.form['name'], user_id=login_session['user_id'])
		session.add(newCloset)
		flash('New Closet %s Successfully Created' % newCloset.name)
		session.commit()
		return redirect(url_for('showClosets'))
	else:
		return render_template('newCloset.html')

# EDIT a Closet's Name
@app.route('/closet/<int:closet_id>/edit/', methods=['GET', 'POST'])
def editCloset(closet_id):
	editedCloset = session.query(
		Closet).filter_by(id=closet_id).one()
	if 'username' not in login_session:
		return redirect('/login')
	if editedCloset.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this closet. Please create your own closet in order to edit.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		if request.form['name']:
			editedCloset.name = request.form['name']
			flash('Closet Successfully Edited %s' % editedCloset.name)
			return redirect(url_for('showClosets'))
	else:
		return render_template('editCloset.html', closet=editedCloset)

# DELETE a closet
@app.route('/closet/<int:closet_id>/delete/', methods=['GET', 'POST'])
def deleteCloset(closet_id):
	closetToDelete = session.query(
		Closet).filter_by(id=closet_id).one()
	if 'username' not in login_session:
		return redirect('/login')
	if closetToDelete.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to delete this closet. Please create your own closet in order to delete.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		session.delete(closetToDelete)
		flash('%s Successfully Deleted' % closetToDelete.name)
		session.commit()
		return redirect(url_for('showClosets', closet_id=closet_id))
	else:
		return render_template('deleteCloset.html', closet=closetToDelete)

# show image ads
@app.route('/show/<filename>')
def uploaded_file(filename):
    return render_template('template.html', filename=filename)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory('http://127.0.0.1:5000/uploads/', filename)


# Create Category Page to display items in that category
@app.route('/closet/<int:closet_id>/')
@app.route('/closet/<int:closet_id>/items/')
def showItems(closet_id):
	closets = session.query(Closet).filter_by(id=closet_id)
	#creator = getUserInfo(closets.user_id)
	items = session.query(Item).filter_by(closet_id=closet_id).all()

	for closet in items:
		print closet.id
		print closet.name
		print closet.photo_link
		print closet.receipt_image


	return render_template('items.html', items=items, closet_id=closet_id, login_session=login_session)
	##TODO: Make sure limit by user id what items can be viewed
	# if 'username' not in login_session:
	#     return render_template('publicclosets.html', closets=closets)
	# else:
	#     return render_template('item.html', closets=closets)

# Create a new item
@app.route('/closet/<int:closet_id>/item/new/', methods=['GET', 'POST'])
def newItem(closet_id):
	if 'username' not in login_session:
		return redirect('/login')
	closet = session.query(Closet).filter_by(id=closet_id).one()
	if login_session['user_id'] != closet.user_id:
		return "<script>function myFunction() {alert('You are not authorized to add item items to this closet. Please create your own closet in order to add items.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		# Get filename and save w. filesys
		file = request.files['file']

		if file and allowed_file(file.filename):
			fileExt = str(file.filename).split('.')[1]
			print("filext:" + fileExt)
			photo_link = str(session.query(Item).order_by(
				Item.id.desc()).first().id+1) + '.' + fileExt
			print("photo_link:" + photo_link)

			file.save(os.path.join('static/img/item/', photo_link))
			new_link = 'static/img/item/' + photo_link

		file = request.files['receipt_image']

		if file and allowed_file(file.filename):
			fileExt = str(file.filename).split('.')[1]
			print("filext:" + fileExt)
			receipt_image = str(session.query(Item).order_by(
				Item.id.desc()).first().id+1) + '.' + fileExt
			print("receipt_image:" + receipt_image)

			file.save(os.path.join('static/img/receipt/', receipt_image))
			receipt_link = 'static/img/receipt/' + receipt_image


		newItem = Item(name=request.form['name'], 
				description=request.form['description'],
				value=request.form['value'], 
				category=request.form['category'], 
				closet_id=closet_id, 
				user_id=closet.user_id,
				photo_link = new_link,
				receipt_image = receipt_link
				)

		session.add(newItem)
		session.commit()
		flash('New Item %s Item Successfully Created' % (newItem.name))
		return redirect(url_for('showItems', closet_id=closet_id))
	else:
		return render_template('newitem.html', closet_id = closet_id)

# Edit an item
@app.route('/closet/<int:closet_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(closet_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	editedItem = session.query(Item).filter_by(id=item_id).one()
	closet = session.query(Closet).filter_by(id=closet_id).one()
	if login_session['user_id'] != closet.user_id:
		return "<script>function myFunction() {alert('You are not authorized to edit item items to this closet. Please create your own closet in order to edit items.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		if request.form['value']:
			editedItem.value = request.form['value']
		if request.form['category']:
			editedItem.category = request.form['category']  
		if True:
			file = request.files['file']
			if file and allowed_file(file.filename):
				same_id = editedItem.id
				print(same_id)
				fileExt = str(file.filename).split('.')[1]
				photo_link = str(same_id) + '.' + fileExt
				file.save(os.path.join('static/img/item/', photo_link))
				new_link = 'static/img/item/' + photo_link
				editedItem.photo_link = new_link  
		if True:
			file = request.files['receipt_image']
			if file and allowed_file(file.filename):
				same_id = editedItem.id
				fileExt = str(file.filename).split('.')[1]
				receipt_link = str(same_id) + '.' + fileExt
				file.save(os.path.join('static/img/receipt', photo_link))
				new_link = 'static/img/receipt/' + photo_link
				editedItem.receipt_image = new_link  

		# if request.form['file']:
		# 	file = request.files['file']
		# 	if file and allowed_file(file.filename):
		# 		fileExt = str(file.filename).split('.')[1]
		# 		photo_link = str(session.query(Item).order_by(
		# 			Item.id.desc()).first().id+1) + '.' + fileExt
		# 	file.save(os.path.join('static/img/item/', photo_link))
		# 	new_link = 'static/img/item/' + photo_link
		# 	print(new_link)
		# 	editedItem.photo_link = new_link  
		# if request.form['receipt_image']:
		# 	file = request.files['receipt_image']
		# 	if file and allowed_file(file.filename):
		# 		fileExt = str(file.filename).split('.')[1]
		# 		print("filext:" + fileExt)
		# 		receipt_image = str(session.query(Item).order_by(
		# 			Item.id.desc()).first().id+1) + '.' + fileExt
		# 		print("receipt_image:" + receipt_image)
		# 		file.save(os.path.join('static/img/receipt/', receipt_image))
		# 		receipt_link = 'static/img/receipt/' + receipt_image
		# 		editedItem.receipt_image = receipt_link  		
		session.add(editedItem)
		session.commit()
		flash('Item Item Successfully Edited')
		return redirect(url_for('showItems', closet_id=closet_id))
	else:
		return render_template('edititem.html', closet_id=closet_id, item_id=item_id, item=editedItem)

# Delete an item
@app.route('/closet/<int:closet_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(closet_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	closet = session.query(Closet).filter_by(id=closet_id).one()
	itemToDelete = session.query(Item).filter_by(id=item_id).one()
	if login_session['user_id'] != closet.user_id:
		return "<script>function myFunction() {alert('You are not authorized to delete item items to this closet. Please create your own closet in order to delete items.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash('Item Item Successfully Deleted')
		return redirect(url_for('showItems', closet_id=closet_id))
	else:
		return render_template('deleteitem.html', item=itemToDelete)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
