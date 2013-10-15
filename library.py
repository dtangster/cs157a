#!/usr/bin/python

# all the imports
import MySQLdb
from cgi import parse_qs, escape
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://bebdd7a70588f7:a6c7c20c@us-cdbr-east-04.cleardb.com/heroku_59b3847e37c77e1'
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'user'
	uid = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(50))
	email = db.Column(db.String(50))
	phone = db.Column(db.String(12))
	fee = db.Column(db.Float)
	password = db.Column(db.String(128))
	salt = db.Column(db.String(32))
	accesslevel = db.Column(db.String(1))

class Loan(db.Model):
	__tablename__ = 'loan'
	bid = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(50))
	uid = db.Column(db.Integer, primary_key = True)
	overdue = db.Column(db.Boolean)
	loan_date = db.Column(db.Date, primary_key = True)
	due_date = db.Column(db.Date)

class Book(db.Model):
	__tablename__ = 'book'
	bid = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(50))
	author = db.Column(db.String(50))
	pub_date = db.Column(db.Date)
	edition = db.Column(db.Integer)
	copies = db.Column(db.Integer)

class Review(db.Model):
	__tablename__ = 'review'
	bid = db.Column(db.Integer, primary_key = True)
	uid = db.Column(db.Integer, primary_key = True)
	rating_date = db.Column(db.Date, primary_key = True)
	stars = db.Column(db.Integer)
	rater_comment = db.Column(db.String(512))

class Reservation(db.Model):
	__tablename__ = 'reservation'
	bid = db.Column(db.Integer, primary_key = True)
	uid = db.Column(db.Integer, primary_key = True)
	reserve_date = db.Column(db.Date)
	avail_date = db.Column(db.Date)
	status = db.Column(db.String(1))

@app.route('/')
def login():
    return 'Login Page'

@app.route('/users/', methods=['GET'])
def users():
	if request.method == 'GET':
		results = User.query.all()

		json_results = []
		for result in results:
			row = {
				'uid': result.uid,
			    'name': result.name,
			    'email': result.email,
			    'phone': result.phone,
			    'fee': result.fee,
			    'password': result.password,
			    'salt': result.salt,
			    'accesslevel': result.accesslevel
			}

			json_results.append(row)

		return jsonify(items=json_results)

@app.route('/loans/', methods=['GET'])
def loans():
	if request.method == 'GET':
		results = Loan.query.all()

		json_results = []
		for result in results:
			row = {
				'bid': result.bid,
			    'title': result.title,
			    'uid': result.uid,
			    'overdue': result.overdue,
			    'loan_date': result.loan_date,
			    'due_date': result.due_date
			}

			json_results.append(row)

		return jsonify(items=json_results)

@app.route('/books/', methods=['GET'])
def books():
	if request.method == 'GET':
		results = Book.query.all()

		json_results = []
		for result in results:
			row = {
				'bid': result.bid,
			    'title': result.title,
			    'author': result.author,
			    'pub_date': result.pub_date,
			    'edition': result.edition,
			    'copies': result.copies
			}

			json_results.append(row)

		return jsonify(items=json_results)

@app.route('/reviews/', methods=['GET'])
def reviews():
	if request.method == 'GET':
		results = Review.query.all()

		json_results = []
		for result in results:
			row = {
				'bid': result.bid,
			    'uid': result.uid,
			    'rating_date': result.rating_date,
			    'stars': result.stars,
			    'rater_comment': result.rater_comment
			}

			json_results.append(row)

		return jsonify(items=json_results)

@app.route('/reservations/', methods=['GET'])
def reservations():
	if request.method == 'GET':
		results = Reservation.query.all()

		json_results = []
		for result in results:
			row = {
				'bid': result.bid,
			    'uid': result.uid,
			    'reserve_date': result.reserve_date,
			    'avail_date': result.avail_date,
			    'status': result.status
			}

			json_results.append(row)

		return jsonify(items=json_results)

if __name__ == '__main__':
    app.run()
