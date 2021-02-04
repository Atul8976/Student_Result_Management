from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import json
import configparser
current_directory = os.getcwd()
db_config_file_path = current_directory+"\\config\\db_config_internal.ini"
config = configparser.ConfigParser()
config.read(db_config_file_path, encoding='utf-8-sig')

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = config["DB_CONFIG"]["HOST"]
app.config['MYSQL_USER'] = config["DB_CONFIG"]["USER"]
app.config['MYSQL_PASSWORD'] = config["DB_CONFIG"]["PASSWORD"]
app.config['MYSQL_DB'] = config["DB_CONFIG"]["DATABASE"]

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'password' in request.form and 'email' in request.form:
        password = request.form['password']
        email = request.form['email']
        sid = None
        marks_list = None
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE password = % s AND email = % s', (check_password_hash(password,password), email,))
            account = cursor.fetchone()
            sid = account["ID"]
            cursor.execute('SELECT standard,grade,remark,percentage FROM result_data WHERE SID = %s',(str(sid),))
            result = cursor.fetchall()

            #list comprehension

            marks_list = [k for k in result]
            result_list = [*[list(idx.values()) for idx in marks_list]]

            # print(result_list)

            if account and result:
                session['loggedin'] = True
                session['id'] = account['ID']
                session['username'] = account['username']
                session['standard'] = account['standard']
                session['result'] = result_list
                session['length'] = len(result)
                msg = 'Logged in successfully !'
                return render_template('result.html')
            elif account:
                session['loggedin'] = True
                session['id'] = account['ID']
                session['username'] = account['username']
                session['standard'] = account['standard']
                msg = 'Logged in successfully !'
                return render_template('index.html',count=session['standard'],msg=msg)
            else:
                msg = 'Incorrect username / password !'

        except Exception as ex:
            print("Exception While Connecting :"+str(ex))
            msg = 'Incorrect username / password !'

    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('standard',None)
    session.pop('result',None)
    session.pop('length',None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/report')
def result():
    return render_template('result.html')


@app.route('/save', methods=['GET', 'POST'])
def save():
    data = None
    msg=''
    if request.method == "POST":
        req_data = request.form['hid']
        stu_id = request.form['sid']
        print(stu_id)
        data_dict = json.loads(req_data)
        data_dict.pop('submit')
        data_dict.pop('hid')
        data_dict.pop('sid')
        d_list = [k for k in data_dict.values()]
        # dividing list in batch of four
        n = 4
        students_data = [d_list[i:i + n] for i in range(0, len(d_list), n)]
        print(len(students_data))
        marks_list = None
        temp_list = None
        result_data = []
        result_list = None
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM result_data WHERE SID = %s', (stu_id,))
        student_data = cursor.fetchone()
        if student_data:
            msg = 'data alreay present !'
        else:
            try:
                for data in students_data:

                    query = "INSERT INTO result_data(SID,standard,grade,remark,percentage)VALUES(%s,%s,%s,%s,%s)"
                    cursor.execute(query,(stu_id,data[0],data[1],data[2],data[3]))
                    mysql.connection.commit()
                    msg = 'You have successfully registered !'

                cursor.execute('SELECT standard,grade,remark,percentage FROM result_data WHERE SID = % s',(str(stu_id),))

                result = cursor.fetchall()


                # list comprehension

                marks_list = [k for k in result]
                print(marks_list)
                if len(marks_list) == 1:
                    temp_list = [k for k in marks_list[0].values()]
                    print(temp_list)
                    result_data.append(temp_list)
                    result_list = result_data
                else:

                    marks_list = [k for k in result]
                    result_list = [*[list(idx.values()) for idx in marks_list]]
                print(result_list)
                if result:
                    session['loggedin'] = True
                    session['result'] = result_list
                    session['length'] = len(result)
                    msg = 'Logged in successfully !'
                    # return render_template('result.html')

            except Exception as ex:
                print("Exception in statement :"+str(ex))
    return render_template('result.html',msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    msg1 = ''
    # print(msg)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        username = request.form['username']
        rollnumber = request.form['rollnumber']
        email = request.form['email']
        password = request.form['password']
        standard = request.form['currentstd']
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg1 = 'Account already exists !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif not re.match(r'\d+', rollnumber):
                msg = 'Rollnumber must contain only numbers !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$', password):
                msg = 'password must contain atleast one uppercase,lowercase character,one special character and one numberic character with minimum length of 8 digit !'
            elif not re.match(r'\d+', standard):
                msg = 'Standard must contain only numbers !'
            elif not username or not rollnumber or not password or not email or not standard:
                msg = 'Please fill out the form !'
            else:
                cursor.execute('INSERT INTO accounts(username,roll_number,email,password,standard)VALUES (%s,%s,%s,%s,%s)',(username,rollnumber,email,generate_password_hash(password),standard))
                mysql.connection.commit()
                msg1 = 'You have successfully registered !'
                cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
                account = cursor.fetchone()
                session['loggedin'] = True
                session['id'] = account['ID']
                session['username'] = account['username']
                session['standard'] = account['standard']

                return render_template('index.html', msg=msg,msg1=msg1)

        except Exception as ex:
            print("Exception accrued :"+str(ex))
            msg = 'Please fill out the form !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg,msg1=msg1)

app.run('127.0.0.1',50000,debug=True)