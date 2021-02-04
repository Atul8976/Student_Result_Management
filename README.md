# Student_Result_Management

Flask Application That Demonstrate Student Can Register and log in and Maintain Their Score On the Website.

## Installation


```
Perform the following step :

1.create one folder

2. in that folder type following:
   1. git init

   2. git clone https://github.com/Atul8976/Student_Result_Management.git my_app

3. Refer to the "studentmgmt.txt" file for database schema and create a table in MySQL 

4. open the "db_config_internal.ini" from the config folder replace your database connection setting with the existing one


Assuming you have virtualenv created in your system :

1. open the my_app folder in terminal

2. activate "name_of_venv"

3. pip install -r requirements.txt

4. type the following command in the terminal to run the app: "python app.py"

5. type following url in browser : http://localhost:50000/

```

## Usage

```python
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

@app.route('/index')
def index():
    return render_template('index.html')


app.run('127.0.0.1',50000,debug=True)

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
