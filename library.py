#!/usr/bin/python

# all the imports
import MySQLdb
from cgi import parse_qs, escape
from flask import Flask

# create our little application :)
app = Flask(__name__)

def connect_db():
	return MySQLdb.connect("127.0.0.1", "root", "root", "library")

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
