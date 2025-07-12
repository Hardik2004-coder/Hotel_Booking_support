from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_customer_db():
    conn = sqlite3.connect('customer.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_email TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()


def init_owner_db():
    conn = sqlite3.connect('owner.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS owners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT,
        email TEXT UNIQUE,
        contact TEXT,
        password TEXT,
        confirm_password TEXT,
        address TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_name TEXT,
        num_rooms INTEGER,
        location TEXT,
        full_address TEXT,
        wifi INTEGER,
        parking INTEGER,
        owner_email TEXT
    )''')
    conn.commit()
    conn.close()

init_customer_db()
init_owner_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            conn = sqlite3.connect('customer.db')
            c = conn.cursor()
            c.execute('INSERT INTO customers (name, email, password) VALUES (?, ?, ?)', (name, email, password))
            conn.commit()
            return redirect('/customer/login')
        finally:
            conn.close()
    return render_template('customer_signup.html')

@app.route('/customer/feedback', methods=['POST'])
def customer_feedback():
    if 'user_email' not in session:
        return redirect('/customer/login')

    message = request.form['message']
    email = session['user_email']
    conn = sqlite3.connect('customer.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedbacks (customer_email, message) VALUES (?, ?)', (email, message))
    conn.commit()
    conn.close()
    return redirect('/customer/dashboard')


@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('customer.db')
        c = conn.cursor()
        c.execute('SELECT * FROM customers WHERE email = ? AND password = ?', (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = user[1]  
            session['user_email'] = user[2]
            if email == 'marksmantechnology@gmail.com' and password == 'Marksman':
                session['admin'] = True
                return redirect('/admin/dashboard')
            return redirect('/customer/dashboard')
    return render_template('customer_login.html')


@app.route('/owner/form', methods=['GET', 'POST'])
def owner_form():
    if request.method == 'POST':
        owner_name = request.form['owner_name']
        email = request.form['email']
        contact = request.form['contact']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['address']
        hotel_name = request.form['hotel_name']
        num_rooms = request.form['num_rooms']
        location = request.form['location']
        full_address = request.form['full_address']
        wifi = 1 if request.form.get('wifi') == 'on' else 0
        parking = 1 if request.form.get('parking') == 'on' else 0

        if password != confirm_password:
            return redirect('/owner/form')

        try:
            conn = sqlite3.connect('owner.db')
            c = conn.cursor()
            c.execute('''INSERT INTO owners (owner_name, email, contact, password, confirm_password, address) 
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                      (owner_name, email, contact, password, confirm_password, address))
            c.execute('''INSERT INTO hotels (hotel_name, num_rooms, location, full_address, wifi, parking, owner_email) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                      (hotel_name, num_rooms, location, full_address, wifi, parking, email))
            conn.commit()
            return redirect('/owner/login')
        finally:
            conn.close()

    return render_template('hotel_owner_form.html')

@app.route('/owner/login', methods=['GET', 'POST'])
def owner_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('owner.db')
        c = conn.cursor()
        c.execute('SELECT * FROM owners WHERE email = ? AND password = ?', (email, password))
        owner = c.fetchone()
        conn.close()
        if owner:
            session['owner'] = owner[1]  
            session['owner_email'] = owner[2]  
            return redirect('/owner/dashboard')

    return render_template('owner_login.html')

@app.route('/owner/dashboard', methods=['GET', 'POST'])
def owner_dashboard():
    if 'owner_email' not in session:
        return redirect('/owner/login')

    conn = sqlite3.connect('owner.db')
    c = conn.cursor()

    if request.method == 'POST':
        if 'delete_id' in request.form:
            hotel_id = request.form['delete_id']
            c.execute('DELETE FROM hotels WHERE id = ? AND owner_email = ?', (hotel_id, session['owner_email']))
            conn.commit()
            conn.close()
            return redirect('/owner/dashboard') 

        elif 'update_id' in request.form:
            hotel_id = request.form['update_id']
            c.execute('''UPDATE hotels SET hotel_name=?, num_rooms=?, location=?, full_address=?, wifi=?, parking=?
                         WHERE id = ? AND owner_email = ?''', (
                request.form['hotel_name'],
                request.form['num_rooms'],
                request.form['location'],
                request.form['full_address'],
                1 if request.form.get('wifi') == 'on' else 0,
                1 if request.form.get('parking') == 'on' else 0,
                hotel_id,
                session['owner_email']
            ))
            conn.commit()
            conn.close()
            return redirect('/owner/dashboard') 

        elif 'new_hotel' in request.form:
            c.execute('''INSERT INTO hotels (hotel_name, num_rooms, location, full_address, wifi, parking, owner_email)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', (
                request.form['hotel_name'],
                request.form['num_rooms'],
                request.form['location'],
                request.form['full_address'],
                1 if request.form.get('wifi') == 'on' else 0,
                1 if request.form.get('parking') == 'on' else 0,
                session['owner_email']
            ))
            conn.commit()
            conn.close()
            return redirect('/owner/dashboard')  

    c.execute('SELECT * FROM hotels WHERE owner_email = ?', (session['owner_email'],))
    hotels = c.fetchall()
    conn.close()
    return render_template('hotel_owner_dashboard.html', hotels=hotels)


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/customer/login')

    conn1 = sqlite3.connect('owner.db')
    c1 = conn1.cursor()
    c1.execute('SELECT * FROM hotels')
    hotels = c1.fetchall()
    conn1.close()

    conn2 = sqlite3.connect('customer.db')
    c2 = conn2.cursor()
    c2.execute('SELECT * FROM feedbacks')
    feedbacks = c2.fetchall()
    conn2.close()

    return render_template('admin_dashboard.html', hotels=hotels, feedbacks=feedbacks)

@app.route('/admin/delete_hotel', methods=['POST'])
def delete_hotel():
    if 'admin' not in session:
        return redirect('/customer/login')

    hotel_id = request.form['hotel_id']
    conn = sqlite3.connect('owner.db')
    c = conn.cursor()
    c.execute('DELETE FROM hotels WHERE id = ?', (hotel_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/dashboard')

@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user' not in session:
        return redirect('/customer/login')

    conn = sqlite3.connect('owner.db')
    c = conn.cursor()
    c.execute('SELECT hotel_name, num_rooms, location, full_address, wifi, parking FROM hotels')
    hotels = c.fetchall()
    conn.close()

    return render_template('customer_dashboard.html', hotels=hotels)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
# Run app using the command - python app.py
# Run actions.py in chatbot using command - python run actions
# Run model and server in chatbot using command - rasa run --enable-api --cors "*"

# Credentials for admin panel (Non Updated) - email : marksmantechnology@gmail.com, password : Marksman