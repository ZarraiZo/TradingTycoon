import sqlite3

current_user = None

def set_active_user(username):
    global current_user
    current_user = username

def get_active_user():
    global current_user
    return current_user

def clear_active_user():
    global current_user
    current_user = None

def authenticate_user(username, password):
    connection = sqlite3.connect('datenbank.db')
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    connection.close()

    return user is not None