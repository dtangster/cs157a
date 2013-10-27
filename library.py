#!/usr/bin/python

#from redis_session import RedisSessionInterface
import os
import logging
import redis
import gevent
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
redis = redis.from_url('redis://rediscloud:JgbwHrCYL809ZGYF@pub-redis-14252.us-east-1-3.1.ec2.garantiadata.com:14252')

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
    return MySQLdb.connect(host='us-cdbr-east-04.cleardb.com', user='bebdd7a70588f7',
        passwd='a6c7c20c', db='heroku_59b3847e37c77e1')

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
    cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "%s"' % (table))
    headers = cur.fetchall()
    cur.execute('SELECT * FROM %s' % (table))
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

broadcaster = DatabaseBroadcaster()
broadcaster.start()

if __name__ == '__main__':
    app.run(debug="True") # Make sure to remove the parameter before deploying to Heroku.
