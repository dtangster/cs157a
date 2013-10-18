import flask, flask.views
app = flask.Flask(__name__)

import MySQLdb.cursors
from cgi import parse_qs, escape
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

import MySQLdb as mdb

class book(flask.views.MethodView):    
	def get(self):
            con = connect_db()
            cur = con.cursor()
            cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "BOOK"')
            head = cur.fetchall()
            cur.execute("SELECT * FROM BOOK")
            rows = cur.fetchall()
            return render_template('index2.html', entries=rows, headers=head)

class loan(flask.views.MethodView):
    def get(self):
        con = connect_db()
        cur = con.cursor()
        cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "LOAN"')
        head = cur.fetchall()
        cur.execute("SELECT * FROM LOAN")
        rows = cur.fetchall()
        return flask.render_template('index2.html',  entries=rows, headers=head)        


class user(flask.views.MethodView):
    def get(self):
        con = connect_db()
        cur = con.cursor()
        cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "USER"')
        head = cur.fetchall()
        cur.execute("SELECT * FROM USER")
        rows = cur.fetchall()
        return flask.render_template('index2.html',  entries=rows, headers=head)  

def connect_db():
    con = mdb.connect(host='localhost', user='root', passwd='root', db='kim')
    return con


app.add_url_rule('/loan/',
                 view_func=loan.as_view('loan'),
                 methods=['GET'])

app.add_url_rule('/user/',
                 view_func=user.as_view('user'),
                 methods=['GET'])

app.add_url_rule('/book/',
                 view_func=book.as_view('book'),
                 methods=['GET'])

app.add_url_rule('/', view_func=book.as_view('main'))


app.debug = True
app.run()