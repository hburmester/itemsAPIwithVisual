from flask import Flask, request, jsonify, render_template, redirect
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from dotenv import load_dotenv
from db import mysql
import os

load_dotenv()

app = Flask(__name__)

# Flask-JWT-Extended Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
jwt = JWTManager(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("""
                DROP TABLE IF EXISTS items
                """)
    cur.execute("""
                DROP TABLE IF EXISTS users
                """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            description TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            password TEXT
        )
    """)
    cur.execute("""INSERT INTO users (username, password) VALUES ("hburmester", "polo1234");""")
    cur.execute("""INSERT INTO items (name, description) VALUES ("something", "works");""")
    mysql.connection.commit()
    cur.close()

@app.route('/')
def home():
    return redirect('/visual/login')

@app.route('/visual/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        cursor = mysql.connection.cursor()
        user = cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        cursor.commit()
        cursor.close()

        if user:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        
    return render_template("login.html")

@app.route('/visual/items', methods=['GET'])
@jwt_required()
def display_items():

    # Authorization logic can be added here based on user roles
    current_user = get_jwt_identity()
    # Example: Allow only me to access this endpoint
    if current_user != 'hburmester':
        return render_template('unauthorized.html'), 403

    cur = mysql.connect.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    cur.close()
    return render_template('items.html', items=items)
