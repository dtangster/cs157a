#!/usr/bin/python

# all the imports
import MySQLdb
import MySQLdb.cursors
from cgi import parse_qs, escape
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)

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

@app.route('/<table>')
def show_entries(table):
    cur = g.db.cursor()
    cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "%s"' % (table))
    headers = cur.fetchall()
    cur.execute('SELECT * FROM %s' % (table))
    entries = cur.fetchall()
    return render_template('layout.html', headers=headers, entries=entries)

if __name__ == '__main__':
    app.run(debug="True")