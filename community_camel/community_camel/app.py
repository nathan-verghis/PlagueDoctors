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

@app.route('/login', methods = ['POST'])
	conn = get_db()
	req = request.get_json(force = True)
	cur = conn.cursor()
	emailId = req['emailId']
	passWd = req['pass']
	cur.execute("SELECT * from Accounts where emailId = %s AND pass = %s", [emailId, passWd])
	data = len(cur.fetchall())
	status = {}
	if(data != 0):
		session['emailId'] = emailId
		session['logged_in'] = True
		status = dict({'status': "Logged in"})
	else:
		status = dict({'status': "Error"})
	return jsonify(status)

@app.route('/logout', methods = ['POST'])
	session.pop('emailId', None)
	session['logged_in'] = False
	return redirect(url_for('index', name = None))

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
		statis = {}
		if ccv < 100 or ccv > 999:
			status = {'Type': "Error", 'content' : "Invalid CCV"}
			return status
		if isnumeric(phoneNum) and len(phoneNum != 10) == False:
			status = dict({'Type': "Error", 'content' : 'Invalid phone number format'})
			return status
		if (len(emailId) == 0 or len(passWd) == 0 or len(firstN) == 0 or len(lastN) == 0 or len(stAdd) == 0 or len(city) == 0)
			status = dict({'Type': "Error", 'content' : 'Please fill in all the forms'})
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
		session['emailId'] = emailId
		session['logged_in'] = True
		status = {'Type' : "SQL" , 'content' : cur.statusmessage}
		return status

@app.route('/user-create-new-order', methods = ['POST'])
def createorder():
	if request.method == 'POST':
		print("GOT ORDER REQUEST")
		req = request.get_json(force = true)
		numitems = len(req['items'])
		itemsList = req['items']
		status = "NEW"
		orderType = req['ordertype']
		donation = req['donation']
		emailId = session['emailId']
		#get the user address and store it
		conn = get_db()
		cur = conn.cursor()
		cur.execute("SELECT Address FROM Accounts WHERE emailId = %s", [emailId])
		orderadd = cur.fetchone()
		cur.execute("SELECT city FROM Accounts WHERE emailId = %s", [emailId])
		city = cur.fetchone()
		cur.execute("SELECT province FROM Accounts WHERE emailId = %s", [emailId])
		province = cur.fetchone()
		cur.execute("SELECT country FROM Accounts WHERE emailId = %s", [emailId])
		country = cur.fetchone()
		cur.execute("INSERT INTO orderList (numitems, status, type, donation, orderadd, city, emailid, province, country) VALUES (%d, %s, %s, %d, %s, %s, %s, %s) RETURNING orderId")
		conn.commit()
		orderno = cur.fetchone()
		for i in numitems:
			itemname = i.itemName
			itemquant = i.itemQ
			itemStatus = "NEW"
			cur.execute("INSERT INTO orderItem (orderNumber, itemName, quantity, itemStatus, cost) VALUES (%d, %d, %s, %d, %s, 0.0)")
		status = {"status" : cur.statusmessage}
		return status

@app.route('/user-get-my-orders-open', methods = ['GET'])
def getuserorders():
	if request.method == 'GET':
		print("GOT TO ORDER LIST FOR USER")
		emailId  = session['emailId']
		conn = get_db()
		#get all orders
		cur = conn.cursor()
		#get all completed items in order
		statnew = conn.cursor()
		statpen = conn.cursor()
		statcl = con.cursor()
		cur.execute("SELECT orderID FROM orderList WHERE emailId = %s AND status = %s", [emailId, "NEW"])
		orderListInfo = []
		count = 0
		for i in cur.fetchall():
			statnew.execute("SELECT * FROM orderItem WHERE orderID = %s AND itemStatus = %s" [i, "NEW"])
			statpen.execute("SELECT * FROM orderItem WHERE orderID = %s AND itemStatus = %s" [i, "PENDING"])
			statcl.execute("SELECT * FROM orderItem WHERE orderID = %s AND itemStatus = %s" [i, "CLOSED"])
			orderListInfo.append([])
			orderListInfo[count].append([i[0]])
			orderListInfo[count].append(len(statnew.fetchall()))
			orderListInfo[count].append(len(statpen.fetchall()))
			orderListInfo[count].append(len(statcl.fetchall()))
			count += 1
		return orderListInfo

@app.route('/user-get-my-orders-closed', methods = ['GET'])
def getuserorders():
	if request.method == 'GET':
		print("GOT TO ORDER LIST FOR USER")
		emailId  = session['emailId']
		conn = get_db()
		#get all orders
		cur = conn.cursor()
		#get all completed items in order
		cur.execute("SELECT orderID FROM orderList WHERE emailId = %s", [emailId])
		orderListInfo = []
		lenght = 0
		for i in cur.fetchall():
			orderListInfo.append([])
			statcl.execute("SELECT * FROM orderItem WHERE orderID = %s AND itemStatus = %s" [i, "CLOSED"])
			orderListInfo[length].append([i[0]])
			orderListInfo[length].append(len(statnew.fetchall()))
			orderListInfo[length].append(len(statpen.fetchall()))
			orderListInfo[length].append(len(statcl.fetchall()))
			cost = getcost(i[0])
			orderListInfo[length].append(cost)
			length += 1
		return orderListInfo
def getcost(orderNum):
	emailId = session['emailId']
	conn = get_db()
	cur = conn.cursor()
	cost = 0.0
	cur.execute("SELECT cost FROM orderItem WHERE orderID = %s AND itemStatus = %s" [orderId, "CLOSED"])
	for i in cur.fetchall():
		cost += i[0]
	return cost

@app.route('/user-get-order-details', methods = ['POST'])
def getorderinfo
	if request.method == 'POST'
		print("GOT TO ORDER INFO")
		conn = get_db()
		cur = conn.cursor()
		orderId = req['orderId']
		cur.execute("SELECT * FROM orderItem WHERE orderID = %s" [orderId])
		orderInfo = []
		length = 0
		for i in cur.fetchall():
			orderInfo.append([])
			orderInfo[length].append(i[2])
			orderInfo[length].append(i[3])
			orderInfo[length].append(i[4])
			orderInfo[length].append(i[6])
			length += 1
		return orderInfo

@app.route('/driver-get-nearby-orders', methods = ['GET'])
	if request.method == 'GET':
		print("GOT TO ORDER LIST FOR DRIVER")
		emailId  = session['emailId']
		conn = get_db()
		#get all orders
		cur = conn.cursor()
		#get all completed items in order
		statnew = conn.cursor()
		cur.execute("SELECT city, province FROM Accounts where emailId = %s and status = %s", [emailId, "NEW"])
		data = cur.fetchone()
		drivercity = data[0]
		driverprovince = data[1]
		cur.execute("SELECT orderID, address FROM orderList WHERE city = %s AND province = %s AND status = %s", [drivercity, driverprovince, "NEW"])
		orderListInfo = []
		count = 0
		for i in cur.fetchall():
			statnew.execute("SELECT itemName, quantity FROM orderItem WHERE orderID = %s AND itemStatus = %s" [i, "NEW"])
			orderListInfo.append([])
			orderListInfo[count].append([i[0]])
			orderListInfo[count].append([i[1]])
			orderListInfo[count].append((statnew.fetchone)[0])
			orderListInfo[count].append((statnew.fetchone)[1])
			count += 1
		return orderListInfo

@app.route('/driver-active-orders', methods = ['GET'])
	if request.method == 'GET':
		print("GOT TO ORDER LIST FOR DRIVER")
		emailId  = session['emailId']
		conn = get_db()
		#get all orders
		cur = conn.cursor()
		#get all completed items in order
		statnew = conn.cursor()
		cur.execute("SELECT city, province FROM Accounts where emailId = %s and status = %s", [emailId, "NEW"])
		data = cur.fetchone()
		drivercity = data[0]
		driverprovince = data[1]
		cur.execute("SELECT orderNo FROM orderItem WHERE driverEmail = %s", [emailId])
		orderListInfo = []
		count = 0
		statadd = conn.cursor()
		for i in cur.fetchall():
			statnew.execute("SELECT itemName, quantity FROM orderItem WHERE orderID = %s AND driverEmail = %s", [i[0], emailId])
			statadd.execute("SELECT address from orderList WHERE orderID = %s" [i[0]])
			orderListInfo.append([])
			orderListInfo[count].append(i[0])
			orderListInfo[count].append(i[1])
			orderListInfo[count].append(i[2])
			orderListInfo[count].append((statnew.fetchone)[0])
			orderListInfo[count].append((statnew.fetchone)[1])
			count += 1
		return orderListInfo

@app.route('/driver-add-order', methods = ['POST'])
if request.method = 'POST':
	emailId = session['emailId']
	conn = get_db()
	cur = conn.cursor()
	orderName = req['orderName']
	itemName = req['itemName']
	cur.execute("SELECT id FROM orderItem WHERE orderNumber = %s AND itemName = %s", [orderNum, itemName])
	data = cur.fetchall()
	for i in data:
		cur.execute("UPDATE itemList SET driverEmail = %s AND status = %s WHERE id = %s", [emailId, "PENDING", i[0])

@app.route('/driver-delivery', methods = ['POST'])
if request.method = 'POST':
	emailId = session['emailId']
	conn = get_db()
	cur = conn.cursor()
	orderName = req['orderName']
	itemName = req['itemName']
	cur.execute("SELECT id FROM orderItem WHERE orderNumber = %s AND itemName = %s", [orderNum, itemName])
	data = cur.fetchall()
	for i in data:
		cur.execute("UPDATE itemList SET status = %s WHERE id = %s", ["CLOSED", i[0])



'''notes: if we can't figure out google API we can sort by orders in the same city province country of the user 
'''