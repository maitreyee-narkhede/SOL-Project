from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from hashlib import sha256
from flask import jsonify
from flask_mail import*
from random import*
import psycopg2
import os

# Connect to database to store user details an payment details

con = psycopg2.connect(database='myproject',user='maina', password='maina123')
cur = con.cursor()

app = Flask(__name__)
cors = CORS(app)
mail = Mail(app)

app.config["MAIL_SERVER"] = "localhost"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "username@gmail.com"
app.config["MAIL_PASSWORD"] = "***********"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = False

# RSA ENCRYPTION FUNCTIONS

def convertToInt(msg_str):
    res = 0
    for i in range(len(msg_str)):
        res = res * 256 + ord(msg_str[i])
    return res

def powMod(a, n, mod):
    if n == 0:
        return 1 % mod
    elif  n == 1:
        return a % mod
    else:
        b = powMod(a, n // 2, mod)
        b = b * b % mod
        if n % 2 == 0:
            return b
        else:
            return b * a % mod

def encrypt(message):
    modulo = 1110014195838866450995043
    exponent = 767549
    c = convertToInt(message)
    return powMod(c, exponent, modulo)
            
# USER REGISTRATION

@app.route('/register', methods=['POST'])
@cross_origin()
def registration():
    total = "select* from login;"
    insert = "insert into login(srno, username, password, otp) values(%d, '%s', '%s', %d);"    
    username = request.form["username"]
    password = request.form["password"]
    otp = randint(000000,999999)

    if username=='' or password=='':
        object = {'code': 'false',
                  'text': 'Please fill all the text areas.'}
        return jsonify(object)
        
    if username[-10:] == "@gmail.com":
        msg = Message('OTP', sender = "username@gmail.com", recipients = [username])
        msg.body = str(otp)
        #mail.send(msg)
        srno = 1
        cur.execute(total)
        result = cur.fetchall()
        for x in result:
            srno = srno+1
            
        cur.execute("rollback")
        cur.execute(insert % (srno, username, password, otp))
        con.commit()
        print(otp)
        object = {'code': 'true',
                  'text': 'You are registered successfully!'}
        return jsonify(object)
    else:
        object = {'code': 'flase',
                  'text': 'The username entered is incorrect.'}
        return jsonify(object)
            
# USER VALIDATION

@app.route('/validation', methods=['POST'])
@cross_origin()
def validation():
    get_otp = "select otp from login where username='%s';"
    valid = "update login set validate=true where username='%s';"
    user_otp = request.form["otp"]
    username = request.form["username"]
    cur.execute("rollback")
    cur.execute(get_otp % (username))
    result = cur.fetchone()

    if user_otp=='':
        object = {'code': 'false',
                  'text': 'Please enter the OTP.'}
        return jsonify(object)
    
    if result[0] == int(user_otp):
        cur.execute(valid % (username))
        object = {'code': 'true',
                  'text': 'Validation successful'}
        return jsonify(object)
    else:
        object = {'code': 'false',
                  'text': 'OTP Incorrect. Validation not successful.'}
        return jsonify(object)

# USER LOGIN

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    valid = "select username, password,validate from login where username='%s' and password='%s';"
    username = request.form['username']
    password = request.form['password']

    if username=='' or password=='':
        object = {'code': 'false',
                  'text': 'Please fill all the text areas.'}
        return jsonify(object)
    else:
        cur.execute("rollback")
        cur.execute(valid % (username, password))
        result = cur.fetchone()
        if result is None:
            object = {'code': 'false',
                      'text': 'The login details are incorrect. Try again'}
        else:
            if result[0]==username and result[1]==password and result[2]==True: 
                object = {'code': 'true',
                          'text': 'Authentication successful'}
            else:
                object = {'code': 'false',
                          'text': 'Authentication not successful'}
    
        return jsonify(object)

# PAYMENT DETAILS

@app.route('/payment', methods=['POST','GET'])
@cross_origin()
def payment():
    get_srno = "select srno from login where username='%s';"
    insert = "insert into card(id, accountno, phoneno, cardno, cvv) values(%d, '%s', '%s', '%s', '%s');"
    username = request.form["username"]
    account = request.form["account"]
    card = request.form["card"]
    phone = request.form["phone"]
    cvv = request.form["cvv"]

    if account=='' or card=='' or phone=='' or cvv=='':
        object = {'code': 'false',
                  'text': 'Please fill all the text areas.'}
        return jsonify(object)
    else:
        if int(account)<100000000 or int(account)>=1000000000000000:
            object = {'code': 'false',
                      'text': 'Account number entered incorrectly.'}
            return jsonify(object)
        elif int(card)<1000000000000000 or int(card)>9999999999999999:
            object = {'code': 'false',
                      'text': 'Card number entered incorrectly.'}
            return jsonify(object)
        elif int(phone)>9999999999 or int(phone)<1000000000:
            object = {'code': 'false',
                      'text': 'Phone number entered incorrectly.'}
            return jsonify(object)
        elif int(cvv)>999 or int(cvv)<100:
            object = {'code': 'false',
                      'text': 'cvv number entered incorrectly.'}
            return jsonify(object)
        
    cur.execute("rollback")
    cur.execute(get_srno % (username))
    result = cur.fetchone()
    cur.execute(insert % (result[0], encrypt(account), encrypt(phone), encrypt(card), encrypt(cvv)))
    #cur.execute(insert % (result[0], int(encrypt(account)), int(phone)))
    object = {'code': 'true',
              'text': 'Authentication successful'}
    return jsonify(object)

# PIN FOR TRANSACTION

@app.route('/pin', methods=['POST'])
@cross_origin()
def pin_enc():
    add_pin = "update card set pin='%s' where cardno='%s';"
    pin = request.form["pin"]
    card = request.form["card"]
    if pin=='':
        object = {'code': 'false',
                  'text': 'Please enter the pin.'}
        return jsonify(object)
    elif int(pin)>9999 or int(pin)<1000:
        object = {'code': 'false',
                  'text': 'Pin entered incorrectly.'}
        return jsonify(object)
    
    cur.execute("rollback")
    cur.execute(add_pin % (encrypt(pin), encrypt(card)))
    object = {'code': 'true',
              'text': 'Authentication successful'}
    return jsonify(object)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    

    
 
