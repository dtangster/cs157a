#!/usr/bin/python

# all the imports
import MySQLdb
import MySQLdb.cursors
from redis import Redis
from redis_session import RedisSessionInterface
from cgi import parse_qs, escape
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

redis = Redis()
app = Flask(__name__)

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
    cur = g.db.cursor()
    cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "book"')
    headers = cur.fetchall()
    cur.execute('SELECT * FROM book')
    entries = cur.fetchall()
    return render_template('layout.html', headers=headers, entries=entries)   

@app.route('/<table>/', methods=['POST'])
def show_entries(table):
    cur = g.db.cursor()
    cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "%s"' % (table))
    headers = cur.fetchall()
    cur.execute('SELECT * FROM %s' % (table))
    entries = cur.fetchall()
    return render_template('table.html', headers=headers, entries=entries)


if __name__ == '__main__':
    app.run(debug="True")
