#!/usr/bin/python

#from redis_session import RedisSessionInterface
import os
import logging
import psycopg2 as db
import urlparse
import redis
import gevent
import base64
import uuid
import hashlib
from datetime import date
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from cgi import parse_qs, escape
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from flask_sockets import Sockets
from time import gmtime, strftime

app = Flask(__name__)
app.secret_key = "cs157a"
app.debug = 'DEBUG' in os.environ
app.jinja_env.add_extension('jinja2.ext.do')

login_manager = LoginManager()
login_manager.init_app(app)

sockets = Sockets(app)

DATABASE_BROADCASTER = 'broadcaster'
redis = redis.from_url('redis://rediscloud:AYAzvsfo0DSPYjfx@pub-redis-19594.us-east-1-2.3.ec2.garantiadata.com:19594')

# Class used to stream database data to client browser when there are any changes
class DatabaseBroadcaster(object):
    def __init__(self):
        self.clients = list()
        self.broadcaster = redis.pubsub()
        self.broadcaster.subscribe(DATABASE_BROADCASTER)

    def __iter_data(self):
        for message in self.broadcaster.listen():
            data = message.get('data')
            if message['type'] == 'message':
                yield data

    def register(self, client):
        # Register a WebSocket connection for Redis updates.
        self.clients.append(client)

    def send(self, client, data):
        # Send given data to the registered client.
        # Automatically discards invalid connections.
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        # Listens for new messages in Redis, and sends them to clients.
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        # Maintains Redis subscription in the background.
        gevent.spawn(self.run)

@sockets.route('/submit')
def inbox(ws):
    # Receives incoming POST requests and inserts them into Redis.
    while ws.socket is not None:
        # Sleep to prevent *constant* context-switches.
        gevent.sleep(0.1)
        message = ws.receive()
        redis.publish(DATABASE_BROADCASTER, message)

@sockets.route('/receive')
def outbox(ws):
    # Send inserted data to clients via `DatabaseBroadcaster`.
    broadcaster.register(ws)

    while ws.socket is not None:
        # Context switch while `DatabaseBroadcaster.start` is running in the background.
        gevent.sleep()

# Trying to test sessions with a database-like application called Redis.
# It overrides the default session behavior of Flask, but I haven't
# figured out how to use it yet

#app.session_interface = RedisSessionInterface()

# Class used for session management
class User:
    def __init__(self, email, accesslevel=2):
        self.email = email
        self.accesslevel = accesslevel

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.email)

@login_manager.user_loader
def load_user(email):
    email = str(email)
    sql = "SELECT accesslevel FROM user_inf WHERE email = '%s'" % (email)
    db = connect_db()
    cur = db.cursor()
    cur.execute(sql)
    row = cur.fetchone()

    if row is None:
        db.close()
        return None

    accesslevel = row[0]
    db.close()
    return User(email, accesslevel)

@app.route("/logout", methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return show_main_page()

def connect_db():
    return db.connect('host=ec2-54-225-255-208.compute-1.amazonaws.com dbname=d2f7pust9i9q2u user=dfgmdatvkdppay password=dDOdOcyBUU3j4S_5V6NS80N4hf')   
    #return MySQLdb.connect(host='us-cdbr-east-04.cleardb.com', user='bebdd7a70588f7', passwd='a6c7c20c', db='heroku_59b3847e37c77e1')

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/') 
@app.route('/index')
def show_main_page():
    if current_user.is_authenticated():
        if current_user.accesslevel == 2:
            return user()
        elif current_user.accesslevel == 1:
            return lib()
        elif current_user.accesslevel == 0:
            return dba()
    
    table = get_table('available_books')    
    return render_template('anonymous.html', headers=table[0], entries=table[1])

@app.route('/ajax/table_request')
def ajax_table_request():
    tablename = request.args.get('table')

    if request.args.get('bookSpecific') == "True" and request.args.get('userSpecific') == "False":
        bid = int(request.args.get('bid'))        
        table = get_table_book(tablename, bid)
    elif request.args.get('userSpecific') == "False":
        table = get_table(tablename)
    else:   
        table = get_table_user(tablename) # Run this version if userSpecific is set from client

    if current_user.accesslevel == 1:
        if tablename == "book":
            return render_template('libbooktable.html', headers=table[0], entries=table[1])
        elif tablename == "user_inf" or tablename == "user_inf_archive":
            return render_template('libusertable.html', headers=table[0], entries=table[1])

    return render_template('table.html', headers=table[0], entries=table[1], email=current_user.email, accesslevel=current_user.accesslevel)
        
@app.route('/table')
def get_table(table):
    cur = g.db.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'" % (table))
    headers = cur.fetchall()
    cur.execute("SELECT * FROM %s" % (table))
    entries = cur.fetchall()
    return (headers, entries)

# User specific table. We have to make sure this is not called on a table that doesn't have an email field
@app.route('/table_user')
@login_required
def get_table_user(table):
    cur = g.db.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'" % (table))
    headers = cur.fetchall()
    cur.execute("SELECT * FROM %s where email = '%s'" % (table, current_user.email))
    entries = cur.fetchall()
    return (headers, entries)

# Book specific table.
@app.route('/table_book')
@login_required
def get_table_book(table, bid):
    cur = g.db.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'" % (table))
    headers = cur.fetchall()
    cur.execute("SELECT * FROM %s where bid = %d" % (table, bid))
    entries = cur.fetchall()
    return (headers, entries)


@app.route('/query', methods=['POST'])
@login_required
def query():
    try:
        sql = request.form['sql']
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True" # Success

    except:
        g.db.rollback()
        return "False" # Failure

@app.route('/register', methods=['POST'])
def register():
    try:
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        phone = request.form['phone']
        password, salt = hash_password(password)

        sql = "INSERT INTO user_inf (email, name, phone, password, salt, accesslevel) VALUES ('%s', '%s', '%s', '%s', '%s', %d)" \
             % (email, name, phone, password, salt, 2)

        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True" # Success

    except:
        g.db.rollback()
        return "False" # Failure	

@app.route('/profile', methods=['POST'])
@login_required
def get_profile():
    sql = "SELECT name, phone, password FROM user_inf WHERE email = '%s'" % (current_user.email)
    cur = g.db.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    name = row[0]
    phone = row[1]
    password = row[2]
    return jsonify({ "name": name, "phone": phone, "password": password })

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form['name']
    phone = request.form['phone']
    password = request.form['password']
    password, salt = hash_password(password)

    try:
        sql = "UPDATE user_inf SET name = '%s', phone = '%s', password = '%s', salt = '%s' \
            WHERE email = '%s'" % (name, phone, password, salt, current_user.email)

        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"

    except:
        #g.db.rollback()
        return "False"

#borrow_page
@app.route('/borrow_book', methods=['POST']) 
@login_required
def borrow_book():
    try:   
        bid = int(request.form['bid'])
        email = current_user.email
        date = '1111-11-11'   
        sql = "INSERT INTO loan (bid, email, loan_date) VALUES \
               (%d, '%s', '%s')" % (bid, email, date)
        
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"

    except:
        g.db.rollback()
        return "False"

#remove current loan
@app.route('/return_book', methods=['POST'])   
@login_required
def un_borrow_book():
    try: 
        bid = int(request.form['bid'])
        email = current_user.email
        current_date = date.today().isoformat()
        sql = "UPDATE loan SET return_date = '%s' WHERE bid = '%s' \
            and email = '%s'" % (current_date, bid, email)
        
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"

    except:
        g.db.rollback()
        return "False"

#add reservation for a book
@app.route('/reserve_book', methods=['POST'])  
@login_required
def reserve_book():
    try:
        bid = int(request.form['bid'])
        email = current_user.email
        date = strftime("%Y-%m-%d")
        
        sql = "INSERT INTO reservation (bid, email, reserve_date) VALUES \
               (%d, '%s', '%s')" % (bid, email, date)

        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"

    except:
        g.db.rollback()
        return "False";

#remove reservation for a book
@app.route('/un_reserve_book', methods=['POST']) 
@login_required
def un_reserve_book():  
    try:    
        reservation_id = int(request.form['bid'])
        sql = "UPDATE reservation SET status = '%s' WHERE reservation_id = %d" % ("C", reservation_id)
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"

    except:
        g.db.rollback()
        return "False";
        	  
            
#add review/comments to book
@app.route('/add_review', methods=['POST']) 
@login_required
def add_review():  
    try:    
        bid = int(request.form['bid'])
        comment = request.form['comment']
        star = int(request.form['star'])
        date = strftime("%Y-%m-%d")
        email = current_user.email
        
        sql = "insert into review values(%d, '%s', '%s', %d, '%s')" \
               % (bid, email, date, star, comment)
        
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        
        return "True"

    except:
        g.db.rollback()
        return "False";
            
     
   
#waive fee update
@app.route('/waive_fee', methods=['POST']) 
@login_required
def waive_fee():  
    print request.form['email']
    try:    
        email = str(request.form['email'])
   
        sql = "update user_inf set fee = 0 where email='%s'" % (email)
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()        
        return "True"

    except:
        g.db.rollback()
        return "False";
            
#retrieve book data
@app.route('/book_data', methods=['POST']) 
@login_required
def get_book_data():    
    bid = int(request.form['bid'])
    sql = "SELECT title, author, pub_date, edition, copies FROM book WHERE bid = %d" % (bid)
    cur = g.db.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    title = str(row[0])
    author = str(row[1])
    pub_date = str(row[2])
    edition = int(row[3])
    copies = int(row[4])
    return jsonify({ "title": title, "author": author, "pub_date": pub_date, "edition": edition, "copies": copies })

@app.route('/update_book_data', methods=['POST'])
@login_required
def update_book_data():
    bid = int(request.form['bid'])
    title = str(request.form['title'])
    author = str(request.form['author'])
    pub_date = str(request.form['pub_date'])
    edition = int(request.form['edition'])
    copies = int(request.form['copies'])

    try:
        sql = "UPDATE book SET title = '%s', author = '%s', pub_date = '%s', edition = %d, copies = %d \
            WHERE bid = %d" % (title, author, pub_date, edition, copies, bid)

        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"

    except:
        #g.db.rollback()
        return "False"

#extend due date update
@app.route('/extend_dueDate', methods=['POST']) 
@login_required
def extend_dueDate():  
    print request.form['email']
    print (request.form['bid'])
    try:    
        email = str(request.form['email'])
        bid = int(request.form['bid'])
        sql = "update loan set due_date =(select due_date + 7 from loan where email = '%s' and bid = %d) \
               where email='%s' and bid = %d" % (email, bid, email, bid)
               
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()        
        return "True"
    except:
        g.db.rollback()
        return "False";          
    
   
@app.route('/perform_maintenance', methods=['POST']) 
@login_required
def perform_maintenance():
    print "maintainance func"    
    try:    
        sql = "select perform_maintenance()"
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()        
        return "True"
    except:
        g.db.rollback()
        return "False";  
      

#user page
@app.route('/user')		
def user():
    table = get_table("available_books")

    if current_user.is_authenticated():
        return render_template('user.html', headers=table[0], entries=table[1], email=current_user.email, accesslevel=current_user.accesslevel)
    else:
        return render_template('user.html', headers=table[0], entries=table[1])   

#librarian page
@app.route('/lib')	
@login_required
def lib():
    return render_template('lib.html', email=current_user.email, accesslevel=current_user.accesslevel)  

#dba page
@app.route('/dba')	
@login_required	
def dba():
    return render_template('dba.html', email=current_user.email, accesslevel=current_user.accesslevel) 
        
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    if email is None or password is None:
        return "False"

    sql = "SELECT password, salt FROM user_inf WHERE email = '%s'" % (email)
    cur = g.db.cursor()
    cur.execute(sql)
    row = cur.fetchone()

    if row is None:
        return "False"

    valid = verify_password(password, row[0], row[1])
	
    if valid:
        sql = "SELECT accesslevel FROM user_inf where email = '%s'" % (email)
        cur.execute(sql)
        row = cur.fetchone()
        accesslevel = row[0]

        # This line is for logging in the user through Flask-Login 
        login_user(User(email, accesslevel))
        return "True"

    return "False"

def hash_password(password, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
 
    hashed_password = hashlib.sha512(password + salt).hexdigest()
    return (hashed_password, salt)
 
def verify_password(password, hashed_password, salt):
    re_hashed, salt = hash_password(password, salt) 
    return re_hashed == hashed_password

broadcaster = DatabaseBroadcaster()
broadcaster.start()

if __name__ == '__main__':
    app.run(debug="True") # Make sure to remove the parameter before deploying to Heroku.