from flask import request, render_template, redirect, make_response
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies
from flask_mysqldb import MySQL
import os
from db import app, mysql, jwt, commit_query_decorator

@app.route('/')
def home():
    return redirect('/visual/login')

@app.route('/visual/login', methods=['POST', 'GET'])
@commit_query_decorator
def login(cursor):
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            access_token = create_access_token(identity=username)
            # Set the JWT token in the cookie
            response = make_response(redirect('/visual/items'))
            set_access_cookies(response, access_token)
            
            return response
        
    return render_template("login.html")

@app.route('/visual/items', methods=['GET'])
@commit_query_decorator
@jwt_required()
def display_items(cursor):
    try:
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()

        return render_template('items.html', items=items)
    
    except Exception as e:
        print(f"Error fetching items: {str(e)}")

        return render_template("error.html", error_message="Error fetching items")
    
@app.route('/visual/create', methods=['POST', 'GET'])
@commit_query_decorator
@jwt_required()
def create_item(cursor):
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']

            cursor.execute("INSERT INTO items (name, description) VALUES (%s, %s)", (name, description))

            return redirect('/visual/items')
        except Exception as e:
            return render_template("items.html", error_message="Error creating item")
    return render_template("create.html")

@app.route('/visual/delete/<id>', methods=['DELETE'])
@commit_query_decorator
@jwt_required()
def delete_item(cursor, id):
    try:
        cursor.execute("DELETE FROM items WHERE id = %s", id)

        return ''
    except Exception as e:
        return ''