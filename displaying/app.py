from flask import Flask, request, render_template, redirect, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_csrf_token
from datetime import timedelta
from dotenv import load_dotenv
from flask_mysqldb import MySQL
import os

load_dotenv()

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_UNIX_SOCKET'] = os.getenv('MYSQL_UNIX_SOCKET')

mysql = MySQL(app)

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
        cursor.close()

        if user:
            access_token = create_access_token(identity=username)
            return redirect('/visual/items')
        
    return render_template("login.html")

@app.route('/visual/items', methods=['GET'])
# @jwt_required()
def display_items():
    # # Authorization logic can be added here based on user roles
    # current_user = get_jwt_identity()
    # # Example: Allow only me to access this endpoint
    # if current_user != 'hburmester':
    #     return render_template('unauthorized.html'), 403

    try:
        # Establish a database connection
        cur = mysql.connection.cursor()
        
        # Execute the query
        cur.execute("SELECT * FROM items")
        
        # Fetch all items
        items = cur.fetchall()

        # Close the cursor
        cur.close()

        # Render the template with the items data
        return render_template("items.html", items=items)
    except Exception as e:
        # Print the exception for debugging
        print(f"Error fetching items: {str(e)}")
        # Return an error template or message
        return render_template("error.html", error_message="Error fetching items")
