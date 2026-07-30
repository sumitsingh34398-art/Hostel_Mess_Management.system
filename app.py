import sqlite3
import qrcode
import io
from flask import Flask, render_template, request, redirect, url_for, session, send_file

app = Flask(__name__)
app.secret_key = 'hostel_secret_key_secure'

# Database Setup
def init_db():
    conn = sqlite3.connect('hostel.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            name TEXT,
            number TEXT,
            branch TEXT,
            subject TEXT,
            amount REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
do_login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == "admin" and password == "admin123":
        session['admin'] = True
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('hostel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, name, number, branch, subject, amount FROM records ORDER BY id DESC')
    records = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', records=records)

@app.route('/form', methods=['GET', 'POST'])
def student_form():
    if request.method == 'POST':
        import datetime
        timestamp = datetime.datetime.now().strftime("%d %b %Y | %I:%M %p")
        name = request.form.get('name')
        number = request.form.get('number')
        branch = request.form.get('branch')
        subject = request.form.get('subject')
        amount = float(request.form.get('amount', 1500))
        
        conn = sqlite3.connect('hostel.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO records (timestamp, name, number, branch, subject, amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, name, number, branch, subject, amount, 'Paid'))
        conn.commit()
        rec_id = cursor.lastrowid
        conn.close()
        
        return redirect(url_for('receipt', rec_id=rec_id))
    
    return render_template('form.html')

@app.route('/receipt/<int:rec_id>')
def receipt(rec_id):
    conn = sqlite3.connect('hostel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM records WHERE id = ?', (rec_id,))
    rec = cursor.fetchone()
    conn.close()
    return render_template('receipt.html', rec=rec)

@app.route('/generate_qr')
def generate_qr():
    upi_url = "upi://pay?pa=yourhostel@upi&pn=HostelMess&am=1500&cu=INR"
    img = qrcode.make(upi_url)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
