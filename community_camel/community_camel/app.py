from argparse import ArgumentParser, RawTextHelpFormatter
import psycopg2
from psycopg2.errors import SerializationFailure
from flask import Flask, render_template
import requests
import json
import os
from os import path
from flask import jsonify
from flask import session, redirect, url_for
from flask import request

def get_db():
	#parser = ArgumentParser(description = __doc__, formatter_class=RawTextHelpFormatter)
	#parser.add_argument("dsn", 'postgres://appuser:appuserpassword@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/vital-cat-208.defaultdb?sslmode=require')
	#parser.add_argument("-v", "--verbose", action="store_true")
	#opt = parser.parse_args()
	#conn = psycopg2.connect(opt.dsn)
	conn = psycopg2.connect('postgres://appuser:appuserpassword@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/vital-cat-208.defaultdb?sslmode=require')
	return conn

app = Flask(__name__, template_folder = './template')

@app.route('/')
def index(name = None):
	conn = get_db()
	with conn.cursor() as cur:
		cur.execute("SELECT * FROM defaultdb.INFORMATION_SCHEMA.tables where table_TYPE = 'BASE TABLE';")
		print(cur.statusmessage)
	#CHANGE THIS BACK TO INDEX LATER
	return render_template('signup.html', name = name);

@app.route('/signup', methods = ['POST'])
def createacc():
	if request.method == 'POST':
		print("GOT USER")
		req = request.get_json(force = true)
		emailId  = req['email']
		passWd = req['pass']
		phoneNum = req['phoneNum']
		firstN = req['firstName']
		lastN = req['lastName']
		stAdd = req['stAdd']
		suiteNum = req['suiteNum']
		city = req['city']
		prov = req['province']
		country = req['country']
		cardnum = req['cardnum']
		ccv = req['ccv']
		cardexM = req['cardexM']
		cardExY = req['cardExY']
		accType = req['accType']
		confirmPass = req['conPass']
		address = stAdd + ", " + suiteNum + ", " + city + ", " + province + ", " + country
		conn = get_db()
		result = 0
		if ccv < 100 or ccv > 999:
			status = {'Type': "Error", 'content' : 'Invalid CCV'}
			return status
		if isnumeric(phoneNum) and len(phoneNum != 10) == False:
			status = {'Type': "Error", 'content' : 'Invalid phone number format'}
			return status
		if (len(emailId) == 0 or len(passWd) == 0 or len(firstN) == 0 or len(lastN) == 0 or len(stAdd) == 0 or len(city) == 0)
			status = {'Type': "Error", 'content' : 'Please fill in all the forms'}
			return status
		if conpass != passWd:
			status = {'Type': "Error", 'content' : 'password confirmation does not match original password'}
			return status
		cur = conn.cursor()
		cur.execute("SELECT * from Accounts WHERE emailId = %s", [emailId])
		result = len(cur.fetchall())
		if result == 0:
			cur.execute("INSERT INTO Accounts (emailId, pass, phoneNum, firstName, lastName, Address, cardNum, ccv, cardExpMon, cardExpYr, accType, city, province, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %d, %d, %d, %s, %s, %s, %s)")
		conn.commit()
		print(cur.statusmessage)
		status = {'Type' : "SQL" , 'content' : cur.statusmessage}
		return status

@app.route('/user-create-new-order')
def createorder():
	if request.method == 'POST':
		print("GOT ORDER REQUEST")
		req = request.get_json(force = true)
		numitems = len(req['items'])
		status = "NEW"
		orderType = req['ordertype']
		donation = req['donation']
		emailId = req['emailId']
		#get the user address and store it
		conn = get_db()
		cur = conn.cursor()
		cur.execute("SELECT Address FROM Accounts WHERE emailId = %s" emailId)
		orderadd = cur.fetchone()
		cur.execute("SELECT city FROM Accounts WHERE emailId = %s" emailId)
		city = cur.fetchone()
		cur.execute("SELECT province FROM Accounts WHERE emailId = %s" emailId)
		province = cur.fetchone()
		cur.execute("SELECT country FROM Accounts WHERE emailId = %s" emailId)
		country = cur.fetchone()
		cur.execute("INSERT INTO orderList (orderno, numitems, status, type, donation, orderadd, city, emailid, province, country) VALUES (%d, %d, %s, %s, %d, %s, %s, %s, %s)")
		result = 0

'''notes: if we can't figure out google API we can sort by orders in the same city province country of the user
'''