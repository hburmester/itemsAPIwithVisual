from flask import jsonify, Flask
from functools import wraps
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_UNIX_SOCKET'] = os.getenv('MYSQL_UNIX_SOCKET')

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


