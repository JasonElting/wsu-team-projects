#!flask/bin/python

#References and Citations:
#http://flask.pocoo.org/docs/0.12/tutorial/
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
#Favicon: By BomSymbols; https://www.iconfinder.com/icons/2633201/camera_drone_helicopter_spy_technology_icon#size=256; License: Commercial Free with Attribution

#Notice: Much of this code is directly copied from the above links in order to provide a starting framework for the project. Additional features, parameters and customizations 
#were added on top of that code in order to meet funtionality required for the project.

#imports
import os
import sqlite3
import shelve
from flask import Flask, jsonify, request, session, g, redirect, url_for,abort, render_template, flash, send_file
#from flask_httpauth import HTTPBasicAuth

app=Flask(__name__)

debug = True

#auth = HTTPBasicAuth()

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

#conection function for inventory database
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

#conection function for inventory returned databse
def connect_returned():
    rv = sqlite3.connect(app.config['DATABASE2'])
    rv.row_factory = sqlite3.Row
    return rv

#database initialization script for inventory database
def init_db():
    db = get_db()
    with app.open_resource('schema.sql',mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

#database initialization script for inventory returned database
def init_returned():
    db = get_returned()
    with app.open_resource('schema2.sql',mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

#database initialization function for inventory as well as inventory returned database
@app.cli.command('initdb')
def initdb_command():
    init_db()
    init_returned()
    print('Initialized the database.')

#returns the inventory database
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#returns the inventory returned database
def get_returned():
    if not hasattr(g,'returned_db'):
        g.returned_db = connect_returned()
    return g.returned_db

#function that clears the inventory returned database after server refresh (start and stop)
@app.before_first_request
def activate_job():
    db = get_returned()
    db.execute('delete from entries')
    db.commit()

#runs at teardown for both inventory and inventory returned databases
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    if hasattr(g, 'returned_db'):
        g.returned_db.close()

#page for flight control (rendered using 'flight.html' template)
@app.route('/rfid/api/v1/flight', methods=['GET'])
#@auth.login_required
def flight():
    return render_template('flight.html')

#page for about (rendered using 'about.html' template)
@app.route('/rfid/api/v1/about', methods=['GET'])
#@auth.login_required
def about():
    return render_template('about.html')

#page for inventory returned (rendered using 'show_entries.html' template)
@app.route('/rfid/api/v1/inventory', methods=['GET'])
#@auth.login_required
def get_inventory():
    db = get_returned()
    cur = db.execute('select title, tag, location from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html',entries=entries) #display the returned results

#page for inventory (rendered using 'database_updated.html' template)
@app.route('/rfid/api/v1/database', methods=['GET'])
#@auth.login_required
def get_database():
    db=get_db()
    cur = db.execute('select title, tag, location from entries order by id desc')
    entries = cur.fetchall()
    return render_template('database_updated.html',entries=entries) #display the returned results

#retrieves a specific item from the returned inventory database (rendered using the 'show_entries.html' template)
@app.route('/rfid/api/v1/inventory/get', methods=['POST'])
#@auth.login_required
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
    curs = db.cursor()
    cur2 = curs.execute('select title, tag, location from entries order by id desc')
    result = cur.fetchone()
    entries = cur2.fetchall()
    return render_template('show_entries.html', entries =entries, result=result)

#returns an entry from the inventory database (rendered using 'database_updated.html' template)
@app.route('/rfid/api/v1/database/get', methods=['POST'])
#@auth.login_required
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
    cur2 = db.execute('select title, tag, location from entries order by id desc')
    result = cur.fetchone()
    entries = cur2.fetchall()
    return render_template('database_updated.html', entries =entries, result=result)

#method for POSTing information to inventory database
@app.route('/rfid/api/v1/inventory', methods=['POST'])
#@auth.login_required
def create_item():
    db  = get_db()
    try:
    	db.execute('insert into entries (title, tag, location) values (?, ?, ?)', 
            [request.form['title'], request.form['tag'], request.form['location']])
    	db.commit()
	flash("New entry successfully created")
    except:
	flash("Entry with same tag number already exists")

    return redirect(url_for('get_database'))

#method for POSTing information to returned inventory tag
@app.route('/rfid/api/v1/inventory/posttag', methods=['POST'])
#@auth.login_required
def create_inventory_item():
    db = get_returned()
    db_database = get_db()
    curs = db_database.cursor()
    curs2 = db.cursor()

    thetag = request.form['tag']
    
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
	db.execute('insert into entries (title, tag, location) values (?, ?, ?)',
            [thetitle, thetag, thelocation])
    db.commit()
    flash('New entry successfully created')
    return redirect(url_for('get_inventory'))

#method for updating an inventory item in the inventory database
@app.route('/rfid/api/v1/inventory/update', methods=['POST'])
#@auth.login_required
def update_item():
    db = get_db()
    tag = request.form['tag']
    title = request.form['title']
    if (title != ''):
    	t = (title,request.form['location'],tag)
    	db.execute('UPDATE entries SET title = ?, location =? where tag = ?',t)
    else:
        t = (request.form['location'],tag)
	db.execute('UPDATE entries SET location =? where tag = ?', t)
    db.commit()
    flash('Record updated successfully if it existed')
    return redirect(url_for('get_database'))

#method for deleting inventory item from the inventory database
@app.route('/rfid/api/v1/inventory/delete', methods=['POST'])
#@auth.login_required
def delete_item():
    db = get_db()
    tag = (request.form['tag'],)
    db.execute('DELETE from entries WHERE tag = ?',tag)
    db.commit()
    flash("Record deleted if it existed")
    return redirect(url_for('get_database'))

@app.route('/rfid/api/v1/inventory/delete_returned_inventory', methods=['POST'])
#@auth.login_required
def delete_returned_inventory():
    db = get_returned()
    db.execute('delete from entries')
    db.commit()
    return redirect(url_for('get_inventory'))

@app.route('/rfid/api/v1/getDatabase', methods=['GET'])
def get_database_file():
    return send_file('/var/www/myflaskapp/mypack/rfid.db',
   	             as_attachment=True)
