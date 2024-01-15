from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_mysqldb import MySQL
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv
import os

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
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
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

# Create a sample table for demonstration
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

# Authentication Endpoint
@app.route('/api/login', methods=['POST'])
@commit_query_decorator
def login(cursor):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        # Create JWT token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Welcome Page Endpoint
@app.route('/', methods=['GET'])
def welcome():
    return jsonify({'Welcome': 'Page'})

# Protected Endpoint Example
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Retrieve All Items
@app.route('/api/resource', methods=['GET'])
@jwt_required()
@commit_query_decorator
def get_all_items(cursor):

    # Authorization logic can be added here based on user roles
    current_user = get_jwt_identity()
    # Example: Allow only me to access this endpoint
    if current_user != 'hburmester':
        return jsonify({'error': 'Unauthorized'}), 403

    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return jsonify({'items': items})

# Retrieve a Specific Item
@app.route('/api/resource/<int:item_id>', methods=['GET'])
@jwt_required()
@commit_query_decorator
def get_item(cursor, item_id):
    cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    if item:
        return jsonify({'item': item})
    else:
        return jsonify({'error': 'Item not found'}), 404

# Create a New Item
@app.route('/api/resource', methods=['POST'])
@jwt_required()
@commit_query_decorator
def create_item(cursor):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    cursor.execute("INSERT INTO items (name, description) VALUES (%s, %s)", (name, description))

    return jsonify({'message': 'Item created successfully'}), 201

# Update an Existing Item
@app.route('/api/resource/<int:item_id>', methods=['PUT'])
@jwt_required()
@commit_query_decorator
def update_item(cursor, item_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    cursor.execute("UPDATE items SET name=%s, description=%s WHERE id=%s", (name, description, item_id))

    return jsonify({'message': 'Item updated successfully'})

# Partial Update of an Item (PATCH)
@app.route('/api/resource/<int:item_id>', methods=['PATCH'])
@jwt_required()
@commit_query_decorator
def partial_update_item(cursor, item_id):
    data = request.get_json()
    description = data.get('description')

    cursor.execute("UPDATE items SET description=%s WHERE id=%s", (description, item_id))

    return jsonify({'message': 'Item partially updated successfully'})

# Delete an Item
@app.route('/api/resource/<int:item_id>', methods=['DELETE'])
@jwt_required()
@commit_query_decorator
def delete_item(cursor, item_id):
    cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))

    return jsonify({'message': 'Item deleted successfully'})