from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from jinja2 import*
from flask import jsonify
import psycopg2
import os

# Connect to database to store user details an payment details

con = psycopg2.connect(database='myproject',user='maina', password='maina123')
cur = con.cursor()

app = Flask(__name__)
cors = CORS(app)

# USER LOGIN

#@app.route('/login_sql', methods=['POST'])
#@cross_origin()
#def login_sql():
#    return render_template('login_details.html')
        
@app.route('/login_details', methods=['POST'])
@cross_origin()
def login_details():
    valid = "select* from login where password='pwd' or 1=1;"
    username = request.form['username']
    password = request.form['password']
    
    cur.execute("rollback")
    cur.execute(valid)
    result = cur.fetchall()
    print(result)
    return render_template("login_details.html",data = result)



# SQL INJECTION

@app.route('/sql_attack', methods=['POST'])
@cross_origin()
def sql_attack():
    print("$$$$")
    get_data = "select* from card;"
    cur.execute("rollback")
    cur.execute(get_data)
    result = cur.fetchall()
    print(result)
    object = {'code': 'true',
              'list':result,
              'text': 'successful'}
    return jsonify(object)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    

    
 
