#!/usr/bin/python

# all the imports
import MySQLdb
import MySQLdb.cursors
from cgi import parse_qs, escape
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import flask.views

app = Flask(__name__)

class book(flask.views.MethodView):
	def get(self):
            con = connect_db()
            cur = con.cursor()
            cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "BOOK"')
            head = cur.fetchall()
            cur.execute("SELECT * FROM BOOK")
            rows = cur.fetchall()
            return render_template('login.html', entries=rows, headers=head)

class loan(flask.views.MethodView):
    def get(self):
        con = connect_db()
        cur = con.cursor()
        cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "LOAN"')
        head = cur.fetchall()
        cur.execute("SELECT * FROM LOAN")
        rows = cur.fetchall()
        return flask.render_template('login.html',  entries=rows, headers=head)        


class user(flask.views.MethodView):
    def get(self):
        con = connect_db()
        cur = con.cursor()
        cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "USER"')
        head = cur.fetchall()
        cur.execute("SELECT * FROM USER")
        rows = cur.fetchall()
        return flask.render_template('login.html',  entries=rows, headers=head)  



class index(flask.views.MethodView):
    def get(self):  
        return render_template('login.html')

    @app.route('/<table>')
    def show_entries(table):
        return control.select_table(table)

    @app.before_request
    def before_request():
        g.db = connect_db()

    @app.teardown_request
    def teardown_request(exception):
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()


@app.route('/<table>')
def select_table(table):
    cur = g.db.cursor()
    cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "%s"' % (table))
    headers = cur.fetchall()
    cur.execute('SELECT * FROM %s' % (table))
    entries = cur.fetchall()
    return render_template('layout.html', headers=headers, entries=entries)

def connect_db():
    return  MySQLdb.connect(host='localhost', user='root', passwd='root', db='kim')


app.add_url_rule('/', view_func=index.as_view('main'))
app.add_url_rule('/loan/', view_func=loan.as_view('loan'), methods=['GET'])
app.add_url_rule('/user/', view_func=user.as_view('user'), methods=['GET'])
app.add_url_rule('/book/', view_func=book.as_view('book'), methods=['GET'])



if __name__ == '__main__':
    app.run(debug="True")
