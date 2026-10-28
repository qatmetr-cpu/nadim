import sqlite3
import hashlib
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_NAME = "dvcrypt.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS cards (
                        card_number TEXT PRIMARY KEY,
                        customer_name TEXT,
                        status TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT,
                        role TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_name TEXT,
                        card_number TEXT,
                        months INTEGER,
                        price REAL,
                        date TEXT)''')
    
    # تعيين حساب المسؤول الجديد Nadim مع تشفير كلمة المرور Ofsad
    cursor.execute("SELECT * FROM users WHERE username = 'Nadim'")
    if not cursor.fetchone():
        secure_pass = hash_password("Ofsad")
        cursor.execute("INSERT INTO users VALUES ('Nadim', ?, 'admin')", (secure_pass,))
        
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "ALSAFA TV Secure Bridge Running"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hashed_pass = hash_password(password)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, hashed_pass))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "role": user[0], "message": "تم تسجيل الدخول بنجاح"})
    else:
        return jsonify({"success": False, "message": "خطأ في اسم المستخدم أو كلمة المرور"}), 401

@app.route('/add_agent', methods=['POST'])
def add_agent():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم وكلمة المرور"}), 400

    hashed_pass = hash_password(password)
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'agent')", (username, hashed_pass))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"تمت إضافة الوكيل {username} بنجاح"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "اسم المستخدم موجود مسبقاً"}), 400

@app.route('/pay', methods=['POST'])
def pay_card():
    data = request.json
    card_no = data.get('card_number')
    months = int(data.get('months'))
    price = float(data.get('price'))
    agent_name = data.get('agent_name')
    date_today = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE cards SET status = 'Active' WHERE card_number = ?", (card_no,))
    cursor.execute("INSERT INTO transactions (agent_name, card_number, months, price, date) VALUES (?, ?, ?, ?, ?)",
                   (agent_name, card_no, months, price, date_today))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"تم تجديد الكرت {card_no} بنجاح"})

@app.route('/admin_stats', methods=['GET'])
def admin_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # إحصائيات الوكلاء (عدد الكروت وإجمالي المبالغ لكل وكيل)
    cursor.execute('''SELECT agent_name, COUNT(*), SUM(price) FROM transactions GROUP BY agent_name''')
    agents_data = [{"agent": row[0], "cards_count": row[1], "total_sales": row[2]} for row in cursor.fetchall()]
    
    # الأرباح اليومية لتاريخ اليوم
    date_today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''SELECT SUM(price) FROM transactions WHERE date = ?''', (date_today,))
    daily_res = cursor.fetchone()
    daily_profit = daily_res[0] if daily_res[0] else 0
    
    conn.close()
    return jsonify({"success": True, "agents": agents_data, "daily_profit": daily_profit})

if __name__ == '__main__':
    init_db()
    print("ALSAFA TV Server running on port 5000...")
    app.run(host='0.0.0.0', port=5000)
