from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from jinja2 import*
from flask import jsonify
import psycopg2
import os

con = psycopg2.connect(database='myproject',user='maina', password='maina123')
cur = con.cursor()

app = Flask(__name__)
cors = CORS(app)

@app.route('/login_details', methods=['POST'])
@cross_origin()
def login_details():
    valid = "select* from login where password='pwd' or 1=1;"
    username = request.form['username']
    password = request.form['password']  
    cur.execute("rollback")
    cur.execute(valid)
    result = cur.fetchall()
    object = {'list': result}
    return jsonify(object)

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    valid = "select username, password,validate from login where username='%s';"
    username = request.form['username']
    password = request.form['password']

    if username=='' or password=='':
        object = {'code': 'false',
                  'text': 'Please fill all the text areas.'}
        return jsonify(object)
    else:
        cur.execute("rollback")
        cur.execute(valid % (username))
        result = cur.fetchone()
        if result=='':
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

@app.route('/payment_sql', methods=['POST'])
@cross_origin()
def payment_sql():
    get_data = "select* from card;"
    cur.execute("rollback")
    cur.execute(get_data)
    result = cur.fetchall()
    object = {'code': 'true',
              'list':result,
              'text': 'successful'}
    return jsonify(object)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    

    
 
