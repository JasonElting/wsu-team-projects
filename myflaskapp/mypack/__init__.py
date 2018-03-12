#!flask/bin/python

#References and Citations:
#http://flask.pocoo.org/docs/0.12/tutorial/
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
#Favicon: By BomSymbols; https://www.iconfinder.com/icons/2633201/camera_drone_helicopter_spy_technology_icon#size=256; License: Commercial Free with Attribution
#Authentication: http://flask.pocoo.org/snippets/8/

#Notice: Much of this code is directly copied from the above links in order to provide a starting framework for the project. Additional features, parameters and customizations 
#were added on top of that code in order to meet funtionality required for the project.

#imports
import os
import sqlite3
import logging
from flask import Flask, jsonify, request, session, g, redirect, url_for,abort, render_template, flash, send_file, Response
from functools import wraps

app=Flask(__name__)

debug = True

app.config.from_object(__name__)

#database configuration parameters
app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'rfid.db'),
    DATABASE2=os.path.join(app.root_path,'returned.db'),
    SECRET_KEY = 'development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('RFID_SETTINGS',silent=True)

#logging file setup
logging.basicConfig(filename='app.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

#conection function for inventory database
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    #logging.info("connection to main database returned")
    return rv

#conection function for inventory returned databse
def connect_returned():
    rv = sqlite3.connect(app.config['DATABASE2'])
    rv.row_factory = sqlite3.Row
    #logging.info("connection to returned inventory returned")
    return rv

#database initialization script for inventory database
def init_db():
    db = get_db()
    with app.open_resource('schema.sql',mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    #logging.info("main database initialized")

#database initialization script for inventory returned database
def init_returned():
    db = get_returned()
    with app.open_resource('schema2.sql',mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    #logging.info("returned inventory database initialized")

#database initialization function for inventory as well as inventory returned database
@app.cli.command('initdb')
def initdb_command():
    init_db()
    init_returned()
    print('Initialized the database.')
    #logging.info("databases initialized")

#returns the inventory database
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    #logging.info("get main database")

#returns the inventory returned database
def get_returned():
    if not hasattr(g,'returned_db'):
        g.returned_db = connect_returned()
    return g.returned_db
    #logging.info("get returned inventory")

#function that clears the inventory returned database after server refresh (start and stop)
@app.before_first_request
def activate_job():
    db = get_returned()
    db.execute('delete from entries')
    db.commit()
    logging.info("application starting")
    logging.info("returned inventory cleared")

#runs at teardown for both inventory and inventory returned databases
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    if hasattr(g, 'returned_db'):
        g.returned_db.close()
    #logging.info("application teardown")

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if (username == 'drone' and password == '36024pAbxHY'):
	return True
    if (username == 'jameson' and password == 'morgan18!'):
	return True
    else:
	return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

#wrapper for authorization control
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#page for flight control (rendered using 'flight.html' template)
@app.route('/rfid/api/v1/flight', methods=['GET'])
@requires_auth
def flight():
    #gets user credentials
    auth = request.authorization
    logging.info("%s accessed the flight control page", auth.username)
    return render_template('flight.html')

#page for about (rendered using 'about.html' template)
@app.route('/rfid/api/v1/about', methods=['GET'])
@requires_auth
def about():
    #gets user credentials
    auth = request.authorization
    logging.info("%s accessed the about page", auth.username)
    return render_template('about.html')

#page for inventory returned (rendered using 'show_entries.html' template)
@app.route('/rfid/api/v1/inventory', methods=['GET'])
@requires_auth
def get_inventory():
    
    db = get_returned()
    cur = db.execute('select title, tag, location from entries order by id desc')
    entries = cur.fetchall()
    
    #gets login credentials
    auth = request.authorization
    logging.info("%s accessed the inventory page",auth.username)
    return render_template('show_entries.html',entries=entries) #display the returned results

#page for inventory (rendered using 'database_updated.html' template)
@app.route('/rfid/api/v1/database', methods=['GET'])
@requires_auth
def get_database():
    db=get_db()
    cur = db.execute('select title, tag, location from entries order by id desc')
    entries = cur.fetchall()
    
    #gets login credentials
    auth = request.authorization
    logging.info("%s accessed the main database page", auth.username)
    return render_template('database_updated.html',entries=entries) #display the returned results

#retrieves a specific item from the returned inventory database (rendered using the 'show_entries.html' template)
@app.route('/rfid/api/v1/inventory/get', methods=['POST'])
@requires_auth
def get_item():
    db = get_returned()
    curs = db.cursor()
    theid = ''#request.form['id']
    thetag = request.form['tag']

    if (thetag == ''):
        t = (theid,)
        query = 'SELECT * FROM entries WHERE id=?'
    if (theid == ''):
        t = (thetag,)
        query = 'SELECT * FROM entries WHERE tag=?'

    cur = curs.execute(query,t)
    #get the results of the scanned items as well (otherwise we loose the scanned items on the display)
    curs = db.cursor()
    cur2 = curs.execute('select title, tag, location from entries order by id desc')
    result = cur.fetchone()
    entries = cur2.fetchall()

    #gets login credentials
    auth = request.authorization
    logging.info('%s searched for tag %s in returned inventory, result = %s', auth.username, thetag, result != None)
    return render_template('show_entries.html', entries =entries, result=result)

#returns an entry from the inventory database (rendered using 'database_updated.html' template)
@app.route('/rfid/api/v1/database/get', methods=['POST'])
@requires_auth
def get_database_item():
    db = get_db()
    curs = db.cursor()
    theid = ''#request.form['id']
    thetag = request.form['tag']
 
    if (thetag == ''):
        t = (theid,)
        query = 'SELECT * FROM entries WHERE id=?'
    if (theid == ''):
        t = (thetag,)
        query = 'SELECT * FROM entries WHERE tag=?'

    cur = curs.execute(query,t)

    #get all the results of the main database (otherwise we loose the items on the display)
    cur2 = db.execute('select title, tag, location from entries order by id desc')
    result = cur.fetchone()
    entries = cur2.fetchall()

    #gets login credentials
    auth = request.authorization
    logging.info("%s searched for tag %s in main database, result = %s", auth.username, thetag, result != None)
    return render_template('database_updated.html', entries =entries, result=result)

#method for POSTing information to inventory database
@app.route('/rfid/api/v1/inventory', methods=['POST'])
@requires_auth
def create_item():
    result = False
    db  = get_db()
    try:
    	db.execute('insert into entries (title, tag, location) values (?, ?, ?)', 
            [request.form['title'], request.form['tag'], request.form['location']])
    	db.commit()
        result = True
	flash("New entry successfully created")
    except:
	flash("Entry with same tag number already exists")

    #gets login credentials
    auth = request.authorization
    logging.info("%s created item (Title: %s, Tag: %s, Location: %s), result = %s",auth.username,request.form['title'],request.form['tag'],request.form['location'],result) 
    return redirect(url_for('get_database'))

#method for POSTing information to returned inventory tag
@app.route('/rfid/api/v1/inventory/posttag', methods=['POST'])
@requires_auth
def create_inventory_item():
    db = get_returned()
    db_database = get_db()
    curs = db_database.cursor()
    curs2 = db.cursor()

    thetag = request.form['tag']
    
    result = False
    try:
        if (thetag !=''):
            t = (thetag,)
            u = (thetag,)
            query = 'SELECT title FROM entries WHERE tag=?'
            query2 = 'SELECT location FROM entries WHERE tag=?'
    
    	cur = curs.execute(query, t)
    	curs = db_database.cursor()
    	cur2 = curs.execute(query2, u)
    
    	thetitle = str(cur.fetchone()[0])
    	thelocation = str(cur2.fetchone()[0])  
  
    	if (thetitle != ''):
            db.execute('insert into entries (title, tag, location) values (?, ?, ?)', [thetitle, thetag, thelocation])
    	
        db.commit()
    	result = True
    	flash('New entry successfully created')
    except:
    	result = False
   
    #gets login credentials
    auth = request.authorization
    logging.info("%s posted tag %s, result = %s",auth.username, thetag, result)
    return redirect(url_for('get_inventory'))

#method for updating an inventory item in the inventory database
@app.route('/rfid/api/v1/inventory/update', methods=['POST'])
@requires_auth
def update_item():
    db = get_db()
    tag = request.form['tag']
    title = request.form['title']
    
    #test if exists
    curs = db.cursor()
    query = 'SELECT * FROM entries WHERE tag = ?'
    t = (tag,)
    cur = curs.execute(query, t)
    result = cur.fetchone()

    if (title != ''):
    	t = (title,request.form['location'],tag)
    	db.execute('UPDATE entries SET title = ?, location =? where tag = ?',t)
    else:
        t = (request.form['location'],tag)
	db.execute('UPDATE entries SET location =? where tag = ?', t)
    db.commit()
    flash('Record updated successfully if it existed')
    
    #gets login credentials
    auth = request.authorization
    logging.info('%s updated item (Title: %s, Tag: %s, Location: %s), result = %s', auth.username, title, tag, request.form['location'], result != None)
    return redirect(url_for('get_database'))

#method for deleting inventory item from the inventory database
@app.route('/rfid/api/v1/inventory/delete', methods=['POST'])
@requires_auth
def delete_item():
    db = get_db()
    tag = (request.form['tag'],)
    
    #test if exists
    curs = db.cursor()
    query = 'SELECT * FROM entries WHERE tag = ?'
    cur = curs.execute(query, tag)
    result = cur.fetchone()
    
    db.execute('DELETE from entries WHERE tag = ?',tag)
    db.commit()
    flash("Record deleted if it existed")

    #gets login credentials
    auth = request.authorization
    logging.info("%s deleted item with tag %s, result = %s", auth.username, request.form['tag'],result != None)
    return redirect(url_for('get_database'))

@app.route('/rfid/api/v1/inventory/delete_returned_inventory', methods=['POST'])
@requires_auth
def delete_returned_inventory():
    db = get_returned()
    db.execute('delete from entries')
    db.commit()

    #gets login credentials
    auth = request.authorization
    logging.info('%s cleared returned inventory database', auth.username)
    return redirect(url_for('get_inventory'))

@app.route('/rfid/api/v1/getDatabase', methods=['GET'])
@requires_auth
def get_database_file():
    #gets login credentials
    auth = request.authorization
    logging.info("%s downloaded the main database", auth.username)
    return send_file('/var/www/myflaskapp/mypack/rfid.db',
   	             as_attachment=True)
