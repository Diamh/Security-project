# Security Project Report

## Project Overview

This project is a simple user management web application developed using Flask and SQLite. The application includes user registration, login, dashboard access, comments, logout, and an admin page.

The main goal of this project is to demonstrate common web application vulnerabilities and show how they can be mitigated using secure coding practices. The project contains two versions of the application:

- `app.py`: Vulnerable version
- `secure_app.py`: Fixed and secure version

The vulnerabilities tested in this project include:

- SQL Injection
- Weak Password Storage
- Cross-Site Scripting (XSS)
- Broken Access Control
- Insecure Communication over HTTP

The secure version applies mitigations such as parameterized queries, bcrypt password hashing, safe output handling, role-based access control, secure session cookie settings, and HTTPS using TLS/SSL.

---

## Project Structure

```text
Security Project/
│
├── app.py
├── secure_app.py
├── users.db
│
├── templates/
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── admin.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

## Requirements

Before running the application, install the required Python packages:

```bash
python3 -m pip install flask
python3 -m pip install bcrypt
python3 -m pip install pyopenssl
```

---

## Steps to Run the Application

### 1. Run the Vulnerable Version

To run the vulnerable version, use:

```bash
python3 app.py
```

Then open the application in the browser:

```text
http://127.0.0.1:5000
```

### 2. Run the Secure Version

To run the secure version, use:

```bash
python3 secure_app.py
```

Then open the application in the browser:

```text
https://localhost:5443
```

Note: The browser may show a “Not Secure” warning because the secure version uses a local self-signed certificate. This is expected during local testing. In production, a trusted TLS/SSL certificate should be used.

---

## Security Testing Instructions

### 1. SQL Injection Test

In the vulnerable version, go to the login page and enter this payload as the username:

```text
' OR '1'='1' --
```

Enter any random input as the password.

Expected vulnerable result: login succeeds and the user is redirected to the dashboard.

In the secure version, use the same payload.

Expected fixed result: login fails because the secure version uses parameterized queries.

---

### 2. Weak Password Storage Test

In the vulnerable version, passwords are stored using weak MD5 hashing.

Expected vulnerable result: short hexadecimal hashes appear in the password column in the database.

In the secure version, passwords are stored using bcrypt.

Expected fixed result: password hashes begin with `$2b$12$`.

---

### 3. Cross-Site Scripting (XSS) Test

Go to the dashboard comment section and enter this payload:

```html
<script>alert("XSS Test")</script>
```

Expected vulnerable result: a browser alert appears.

Expected fixed result: no alert appears, and the script is displayed as normal text.

---

### 4. Access Control Test

In the vulnerable version, log in as a normal user and open:

```text
http://127.0.0.1:5000/admin
```

Expected vulnerable result: the normal user can access the admin page.

In the secure version, log in as a normal user and open:

```text
https://localhost:5443/admin
```

Expected fixed result: the page displays:

```text
Access Denied: Admins only
```

---

### 5. HTTPS and Secure Session Test

The vulnerable version runs over HTTP:

```text
http://127.0.0.1:5000
```

The secure version runs over HTTPS:

```text
https://localhost:5443
```

The secure version also uses secure session cookie settings:

```python
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
```

These settings help protect session cookies by preventing JavaScript access, sending cookies only over HTTPS, and reducing some cross-site risks.

---

## Security Mitigations Summary

| Vulnerability | Mitigation |
|---|---|
| SQL Injection | Parameterized queries |
| Weak Password Storage | bcrypt password hashing |
| XSS | Safe output escaping |
| Broken Access Control | Role-based access control |
| Insecure Communication | HTTPS using TLS/SSL |
| Session Cookie Risk | HttpOnly, Secure, and SameSite cookie settings |

---

## Notes

If login fails in the secure version after using users created in the vulnerable version, delete `users.db` and register a new user in the secure version. This is because the vulnerable version and secure version use different password storage methods.








