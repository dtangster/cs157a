#!/usr/bin/python

# all the imports
import MySQLdb
import MySQLdb.cursors
from cgi import parse_qs, escape
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)

def connect_db():
    return MySQLdb.connect(host='us-cdbr-east-04.cleardb.com', \
        user='bebdd7a70588f7', passwd='a6c7c20c', \
        db='heroku_59b3847e37c77e1', cursorclass=MySQLdb.cursors.DictCursor)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.cursor()
    cur.execute('select name from user')
    entries = [dict(title=row['name']) for row in cur.fetchall()]
    return render_template('layout.html', entries=entries)

if __name__ == '__main__':
    app.run(debug="True")