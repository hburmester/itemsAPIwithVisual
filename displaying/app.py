from flask import Flask, request, render_template, redirect, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, set_access_cookies
from datetime import timedelta
from dotenv import load_dotenv
from flask_mysqldb import MySQL
import os
from db import app, mysql, jwt

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
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM items")
        items = cur.fetchall()
        cur.close()

        return render_template('items.html', items=items)
    
    except Exception as e:
        print(f"Error fetching items: {str(e)}")

        return render_template("error.html", error_message="Error fetching items")
    
@app.route('/visual/create', methods=['POST', 'GET'])
def create_item():
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO items (name, description) VALUES (%s, %s)", (name, description))
            mysql.connection.commit()
            cur.close()
            return redirect('/visual/items')
        except Exception as e:
            return render_template("items.html", error_message="Error creating item")
    return render_template("create.html")

@app.route('/visual/delete/<id>', methods=['DELETE'])
def delete_item(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM items WHERE id = %s", id)
        mysql.connection.commit()
        cur.close()

        return ''
    except Exception as e:
        return ''