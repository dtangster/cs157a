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
import MySQLdb
import MySQLdb.cursors
from cgi import parse_qs, escape
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from flask_sockets import Sockets

app = Flask(__name__)
app.secret_key = "cs157a"
app.debug = 'DEBUG' in os.environ

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

def connect_db():
    return db.connect('host=ec2-54-225-255-208.compute-1.amazonaws.com dbname=d1npi6l3th4urq user=qfhvpdzhjcvodq password=l8_Nng4uRhGwm9zRN21KEo_nCy')   
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
def show_main_page():
    # This is the page returned normally
    table = get_table('book')
    return render_template('index.html', headers=table[0], entries=table[1])   

@app.route('/ajax/table_request')
def ajax_table_request():
    # This is the AJAX response
    table = get_table(request.args.get('table'))
    return render_template('table.html', headers=table[0], entries=table[1])

@app.route('/table/<table>')
def get_table(table):
    cur = g.db.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'" % (table))
    headers = cur.fetchall()
    cur.execute("SELECT * FROM %s" % (table))
    entries = cur.fetchall()

    # Returns headers as index 0 and entries at index 1
    return (headers, entries)

@app.route('/query', methods=['POST'])
def query():
    try:
        sql = request.form['sql']
        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"; # Success

    except:
        g.db.rollback()
        return "False"; # Failure

@app.route('/register', methods=['POST'])
def register():
    try:
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        phone = request.form['phone']
        password, salt = hash_password(password)

        sql = "INSERT INTO user_inf (email, name, phone, password, salt, accesslevel) VALUES ('%s', '%s', '%s', '%s', '%s', %d)" \
             % (email, name, phone, password, salt, 0)

        cur = g.db.cursor()
        cur.execute(sql)
        g.db.commit()
        return "True"; # Success

    except:
        g.db.rollback()
        return "False"; # Failure

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
        accesslevel = str(row[0])
        return accesslevel # Return access level

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


#CREATE PROCEDURE show_reserved_books(IN username VARCHAR(50))
#SELECT bid, title, author, reserve_date, avail_date
#FROM reservation NATURAL JOIN book where email = username
#ORDER BY bid, title, author;
