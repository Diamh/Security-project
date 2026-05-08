
import flask # type: ignore
from flask import Flask, render_template, request, redirect, session # type: ignore
import sqlite3 
import bcrypt #type: ignore
import os


app = flask.Flask(__name__)
app.secret_key = os.urandom(24) #generates random secure bytes


# Secure session cookie settings:
# HTTPONLY prevents JavaScript from accessing the session cookie.
app.config["SESSION_COOKIE_HTTPONLY"] = True
# SECURE ensures the session cookie is only sent over HTTPS.
app.config["SESSION_COOKIE_SECURE"] = True
# SAMESITE helps reduce cross-site request risks.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


conn = sqlite3.connect("users.db")# to create a comments table if it doesn't exist yet. 
conn.execute('''CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    text TEXT NOT NULL
)''')
conn.commit()
conn.close()

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
    username TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' 
              )''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return flask.redirect('/login')




#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']

      

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        
        #looks for matching user in database
        #uses parameterized query to migitate sql injection
        c.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ) 
        user = c.fetchone()
        
        # bcrypt.checkpw() securely verifies whether the entered password matches
        # the stored bcrypt hash. Unlike MD5, bcrypt hashes cannot be compared directly
        # because bcrypt generates a different hash each time due to salting.
        if user and bcrypt.checkpw(password.encode(), user[4].encode()): #find user by username, get the stored bcrypt from the database using user[4], and uses .checkpw to check if they match
            flask.session['username'] = user[0]
            flask.session['first_name'] = user[1]
            flask.session['last_name'] = user[2]
            flask.session['role'] = user[5]
            conn.close()
            return flask.redirect('/dashboard')

        else: 
            conn.close() 
            return '''
            Failed <br><br> 
            <a href="/login">Try Again</a><br>
            <a href="/register">Register</a>
            '''

    return flask.render_template('login.html')


#dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in flask.session:
        return flask.redirect('/login')

    full_name = flask.session['first_name'] + " " + flask.session['last_name']

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    if flask.request.method == 'POST':
        comment = flask.request.form['comment']
        # stored as-is, but Jinja2 auto-escaping at render time prevents XSS
        c.execute("INSERT INTO comments (username, text) VALUES (?, ?)",
                  (flask.session['username'], comment))
        conn.commit()

    c.execute("SELECT username, text FROM comments")
    rows = c.fetchall()
    conn.close()

    comments = [{'user': row[0], 'text': row[1]} for row in rows]

    # SECURE: safe_mode=False means Jinja2 escapes output, scripts won't execute
    return flask.render_template('dashboard.html', username=flask.session['username'],
                                  full_name=full_name, comments=comments, safe_mode=False)
#logout 
@app.route('/logout')
def logout():
    flask.session.clear() #removes everything from session and completely logs users out
    return flask.redirect('/login')


#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        first_name = flask.request.form['first_name']
        last_name = flask.request.form['last_name']
        email = flask.request.form['email']
        username = flask.request.form['username']
        password = flask.request.form['password']

        #hash using bcrypt (secure)
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        try:
            #migitates sql injection using parameterized queries. This ensuring that user input is treated strictly as data and not executable SQL code.
            c.execute(
                """INSERT INTO users
                (username, first_name, last_name, email, password, role)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (username, first_name, last_name, email, hashed_password, "user")
            )
            conn.commit()
            conn.close()
            return flask.redirect('/login')
        
        except:
            conn.close()
            return "Registration failed (username/email may exist)"

    return flask.render_template('register.html')


#admin
@app.route('/admin')
def admin():
    if 'username' not in flask.session:
        return flask.redirect('/login')

    if flask.session.get('role') != 'admin':
        return "Access Denied: Admins only"

    return flask.render_template('admin.html')


if __name__ == '__main__':

    app.run(

        host='localhost',

        port=5443,

        debug=True,

        use_reloader=False,

        ssl_context='adhoc'

    )
