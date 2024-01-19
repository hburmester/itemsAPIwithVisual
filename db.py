from flask import jsonify, Flask
from flask_jwt_extended import JWTManager
from functools import wraps
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_UNIX_SOCKET'] = os.getenv('MYSQL_UNIX_SOCKET')

# Flask-JWT-Extended Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_HTTPONLY'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

jwt = JWTManager(app)

mysql = MySQL(app)

def commit_query_decorator(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        cursor = None
        try:
            # Create a cursor
            cursor = mysql.connection.cursor()

            # Call the original route function
            response = route_function(cursor, *args, **kwargs)

            # Commit the transaction
            mysql.connection.commit()

            # Verify that the query has committed
            print("\n" + "Query has committed successfully!" + "\n")

            # Continue with the original response from the route function
            return response

        except Exception as e:
            print(f'Error executing query: {str(e)}')
            return jsonify(error=f'Error executing query: {str(e)}')

        finally:
            # Close the cursor only if it was successfully created
            if cursor:
                cursor.close()

    return wrapper

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
