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
app.secret_key = "cs157a"

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
    return render_template('layout.html', headers=table[0], entries=table[1])   

@app.route('/ajax/table_request/')
def ajax_table_request():
    # This is the AJAX response
    table = get_table(request.args.get('table'))
    return render_template('table.html', headers=table[0], entries=table[1])

@app.route('/table/<table>/')
def get_table(table):
    cur = g.db.cursor()
    cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "%s"' % (table))
    headers = cur.fetchall()
    cur.execute('SELECT * FROM %s' % (table))
    entries = cur.fetchall()

    # Returns headers as index 0 and entries at index 1
    return (headers, entries)

if __name__ == '__main__':
    app.run(debug="True")
