
import flask # type: ignore
from flask import Flask, render_template, request, redirect, session # type: ignore
import sqlite3 
import hashlib

app = flask.Flask(__name__)
app.secret_key = "s123"  #this is weak but we made it intetionally for the vulnerable version

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

        #hash the entered password before checking
        hashed_password = hashlib.md5(password.encode()).hexdigest()


        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        
        #looks for matching user in database
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{hashed_password}'" #this is a vulnerability - sql injection
        c.execute(query) 
        user = c.fetchone() #get first matching user
        conn.close()

        if user: #if log in is sucessful, it saves user info in session (keeps them logged in)
            flask.session['username'] = user[0]
            flask.session['first_name'] = user[1]
            flask.session['last_name'] = user[2]
            flask.session['role'] = user[5]
            return flask.redirect('/dashboard')

        else: #if login fails, it will show an error message
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
        comment = flask.request.form['comment']  # raw input, not sanitized - XSS vulnerability
        c.execute("INSERT INTO comments (username, text) VALUES (?, ?)",
                  (flask.session['username'], comment))
        conn.commit()

    c.execute("SELECT username, text FROM comments")
    rows = c.fetchall()
    conn.close()

    comments = [{'user': row[0], 'text': row[1]} for row in rows]

    # VULNERABLE: safe_mode=True allows raw HTML/JS to execute in the browser
    return flask.render_template('dashboard.html', username=flask.session['username'],
                                  full_name=full_name, comments=comments, safe_mode=True)
    
#logout 
@app.route('/logout')
def logout():
    flask.session.pop('username', None) #removes user from session (logs them out), but this way is insecure because it only removes the username and leaves the other data
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

        #MD5 hash - insecure
        hashed_password = hashlib.md5(password.encode()).hexdigest() #hasing the password using an insecure method

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        #vulnerable to sql injection - user input is directly inserted into SQL
        #all new registered users are normal users
        query = f"""
        INSERT INTO users (username, first_name, last_name, email, password, role)
        VALUES ('{username}', '{first_name}', '{last_name}', '{email}', '{hashed_password}', 'user') 
        """

        try:
            c.execute(query)
            conn.commit()
            conn.close()
            return flask.redirect('/login')
        except:
            conn.close()
            return "Registration failed (username/email may exist)"

    return flask.render_template('register.html')

@app.route('/admin') #intentionally insecure because any logged-in user can access admin
def admin():
    if 'username' in flask.session:
        return flask.render_template('admin.html')
    else:
        return flask.redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
