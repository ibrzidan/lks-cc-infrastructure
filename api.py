from flask import Flask, request, redirect, url_for, session, jsonify, render_template, Response
import sqlite3
from time import sleep
from datetime import datetime, timedelta
import psycopg2
import io
import csv

# Setup Awal
app = Flask(__name__)
app.secret_key = "your-secret-key"

# Database Configuration
DB_HOST = "your-endpoint-name-rds"
DB_PORT = "your-port-rds"
DB_NAME = "your-database-name-rds"
DB_USER = "your-master-username-rds"
DB_PASSWORD = "your-password-rds"

def get_db_connection(host):
    """Establish a connection to the database"""
    conn = psycopg2.connect(
        host=host,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def cek_user(username, password):
    con = get_db_connection(DB_HOST) # Connect to Database
    cur = con.cursor()
    # Selecting Data in Database
    cur.execute('SELECT username, password FROM users WHERE username=%s and password=%s', (username, password))
    result = cur.fetchone()
    if result:
        return True
    else:
        return False

# Route for Error
@app.errorhandler(400)
def gagal():
    message = {
        'status': 400,
        'pesan': 'Perintah tidak dapat dijalankan: '+request.url,
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp

# Route for Index
@app.route('/')
def index():
    return render_template('index.html')

# Route for Login
@app.route("/login", methods = ["POST"])
def login():
    if request.method == "POST":
        username = request.form['username'] # Data from form input on the Web
        password = request.form['password'] # Data from form input on the Web
        if cek_user(username, password): # Create session
            session['username'] = username
            session['password'] = password
            return redirect(url_for('home'))
        else:
            return render_template('index.html', error="Username atau password salah!")
    else:
        return render_template('index.html')

@app.route("/signup", methods=["POST"])
def signup():
    con = get_db_connection(DB_HOST) # Connect to Database
    cur = con.cursor()
    
    username = request.form['username']
    password = request.form['password']
    
    # Cek apakah username sudah ada
    cur.execute("SELECT * FROM users WHERE username=%s", (username))
    existing_user = cur.fetchone()
    
    if existing_user:
        return "Username is already taken!", 400

    # Simpan user baru
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    con.commit()
    con.close()
    
    return redirect(url_for('index'))

@app.route('/home', methods=['POST', 'GET'])
def home():
    if 'username' in session and 'password' in session:
        con = get_db_connection(DB_HOST) # Connect to Database
        cur = con.cursor()
        cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data WHERE waktu = NOW()::DATE - INTERVAL '7 hours' ORDER BY waktu DESC")
        data = cur.fetchall()
        data_api=[]
        for i in range(0, len(data)) :
            data[i] = list(data[i])
            data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
        for b in (data):
            if b[2] == 3:
                b[2] = 0
            data_api.append({
                'lokasi' : b[0],
                'waktu' : b[1],
                'pergeseran_cm' : b[2],
            })
        return render_template('home.html', data=data, data_api=data_api)
   
    else:
        return redirect(url_for('login'))

@app.route('/download/report_hariini/csv')
def download_report_hariini():
    con = get_db_connection(DB_HOST) # Connect to Database
    cur = con.cursor()
    cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data WHERE waktu = NOW()::DATE - INTERVAL '7 hours' ORDER BY waktu DESC")
    data = cur.fetchall()
    data_api=[]
    for i in range(0, len(data)) :
        data[i] = list(data[i])
        data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
    for b in (data):
        if b[2] == 3:
            b[2] = 0
        data_api.append({
            'lokasi' : b[0],
            'waktu' : b[1],
            'pergeseran_cm' : b[2],
        })
    output = io.StringIO()
    writer = csv.writer(output)
    line = ['Lokasi, Waktu, Pergeseran (cm)']
    writer.writerow(line)
    for bb in data_api:
        line = [bb['lokasi']+','+str(bb['waktu'])+','+str(bb['pergeseran_cm'])]
        writer.writerow(line)
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=dataewshariini.csv"})

@app.route('/semuadata', methods=['POST', 'GET'])
def semuadata():
    if 'username' in session and 'password' in session:
        con = get_db_connection(DB_HOST) # Connect to Database
        cur = con.cursor()
        cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data ORDER BY waktu DESC")
        data = cur.fetchall()
        data_api=[]
        for i in range(0, len(data)) :
            data[i] = list(data[i])
            data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
        for b in (data):
            if b[2] == 3:
                b[2] = 0
            data_api.append({
                'lokasi' : b[0],
                'waktu' : b[1],
                'pergeseran_cm' : b[2],
            })
        return render_template('semuadata.html', data=data, data_api=data_api)
   
    else:
        return redirect(url_for('login'))

@app.route('/download/report_semuadata/csv')
def download_report_semuadata():
    con = get_db_connection(DB_HOST) # Connect to Database
    cur = con.cursor()
    cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data ORDER BY waktu DESC")
    data = cur.fetchall()
    data_api=[]
    for i in range(0, len(data)) :
        data[i] = list(data[i])
        data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
    for b in (data):
        if b[2] == 3:
            b[2] = 0
        data_api.append({
            'lokasi' : b[0],
            'waktu' : b[1],
            'pergeseran_cm' : b[2],
        })
    output = io.StringIO()
    writer = csv.writer(output)
    line = ['Lokasi, Waktu, Pergeseran (cm)']
    writer.writerow(line)
    for bb in data_api:
        line = [bb['lokasi']+','+str(bb['waktu'])+','+str(bb['pergeseran_cm'])]
        writer.writerow(line)
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=dataewssemuadata.csv"})

@app.route('/week', methods=['POST', 'GET'])
def weekdata():
    if 'username' in session and 'password' in session:
        con = get_db_connection(DB_HOST) # Connect to Database
        cur = con.cursor()
        cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data WHERE DATE_TRUNC('WEEK', waktu) = DATE_TRUNC('WEEK', NOW() + INTERVAL '7 hours') ORDER BY waktu DESC")
        data = cur.fetchall()
        data_api=[]
        for i in range(0, len(data)) :
            data[i] = list(data[i])
            data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
        for b in (data):
            if b[2] == 3:
                b[2] = 0
            data_api.append({
                'lokasi' : b[0],
                'waktu' : b[1],
                'pergeseran_cm' : b[2],
            })
        return render_template('week.html', data=data, data_api=data_api)
   
    else:
        return redirect(url_for('login'))

@app.route('/download/report_mingguini/csv')
def download_report_mingguini():
    con = get_db_connection(DB_HOST) # Connect to Database
    cur = con.cursor()
    cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data WHERE DATE_TRUNC('WEEK', waktu) = DATE_TRUNC('WEEK', NOW() + INTERVAL '7 hours') ORDER BY waktu DESC")
    data = cur.fetchall()
    data_api=[]
    for i in range(0, len(data)) :
        data[i] = list(data[i])
        data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
    for b in (data):
        if b[2] == 3:
            b[2] = 0
        data_api.append({
            'lokasi' : b[0],
            'waktu' : b[1],
            'pergeseran_cm' : b[2],
        })
    output = io.StringIO()
    writer = csv.writer(output)
    line = ['Lokasi, Waktu, Pergeseran (cm)']
    writer.writerow(line)
    for bb in data_api:
        line = [bb['lokasi']+','+str(bb['waktu'])+','+str(bb['pergeseran_cm'])]
        writer.writerow(line)
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=dataewsmingguini.csv"})

@app.route('/month', methods=['POST', 'GET'])
def monthdata():
    if 'username' in session and 'password' in session:
        con = get_db_connection(DB_HOST) # Connect to Database
        cur = con.cursor()
        cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data WHERE DATE_TRUNC('MONTH', waktu) = DATE_TRUNC('MONTH', NOW() + INTERVAL '7 hours') ORDER BY waktu DESC")
        data = cur.fetchall()
        data_api=[]
        for i in range(0, len(data)) :
            data[i] = list(data[i])
            data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
        for b in (data):
            if b[2] == 3:
                b[2] = 0
            data_api.append({
                'lokasi' : b[0],
                'waktu' : b[1],
                'pergeseran_cm' : b[2],
            })
        return render_template('month.html', data=data, data_api=data_api)
   
    else:
        return redirect(url_for('login'))

@app.route('/download/report_bulanini/csv')
def download_report_bulanini():
    con = get_db_connection(DB_HOST) # Connect to Database
    cur = con.cursor()
    cur.execute("SELECT lokasi, waktu, pergeseran_cm FROM landslide_data WHERE DATE_TRUNC('MONTH', waktu) = DATE_TRUNC('MONTH', NOW() + INTERVAL '7 hours') ORDER BY waktu DESC")
    data = cur.fetchall()
    data_api=[]
    for i in range(0, len(data)) :
        data[i] = list(data[i])
        data[i][1] = str(datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
    for b in (data):
        if b[2] == 3:
            b[2] = 0
        data_api.append({
            'lokasi' : b[0],
            'waktu' : b[1],
            'pergeseran_cm' : b[2],
        })
    output = io.StringIO()
    writer = csv.writer(output)
    line = ['Lokasi, Waktu, Pergeseran (cm)']
    writer.writerow(line)
    for bb in data_api:
        line = [bb['lokasi']+','+str(bb['waktu'])+','+str(bb['pergeseran_cm'])]
        writer.writerow(line)
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=dataewsbulanini.csv"})

# Route untuk Logout
@app.route('/logout')
def logout():
    session.clear() # Menghapus session
    return redirect(url_for('index'))

# Run Web
if __name__== "__main__":
    app.run(debug=True)
