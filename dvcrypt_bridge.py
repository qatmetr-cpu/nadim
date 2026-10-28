from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

ADMIN_USER = os.environ.get("ADMIN_USER", "Nadim")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "ofsad")

agents_db = {
    ADMIN_USER: ADMIN_PASS
}

cards_cloud_db = {}
audit_logs = []

@app.route('/', methods=['GET'])
def home():
    try:
        # قراءة ملف index.html مباشرة من المجلد الحالي
        if os.path.exists('index.html'):
            with open('index.html', 'r', encoding='utf-8') as f:
                return f.read(), 200
        else:
            return "ملف index.html غير موجود في المستودع", 404
    except Exception as e:
        return str(e), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if username in agents_db and agents_db[username] == password:
        is_admin = (username == ADMIN_USER)
        return jsonify({
            "message": "تم تسجيل الدخول بنجاح",
            "username": username,
            "is_admin": is_admin
        }), 200
    else:
        return jsonify({"message": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401

@app.route('/api/add-agent', methods=['POST'])
def add_agent():
    data = request.json or {}
    admin_user = data.get('admin_user')
    new_name = data.get('new_username')
    new_pass = data.get('new_password')

    if admin_user != ADMIN_USER:
        return jsonify({"message": "غير مسموح إلا للمسؤول الرئيسي بإضافة وكلاء"}), 403

    if not new_name or not new_pass:
        return jsonify({"message": "يرجى إدخال بيانات الوكيل الجديد"}), 400

    agents_db[new_name] = new_pass
    return jsonify({"message": f"تم إضافة الوكيل {new_name} بنجاح"}), 200

@app.route('/api/search', methods=['GET'])
def search_card():
    card_id = request.args.get('card')
    agent = request.args.get('agent', 'unknown')

    if not card_id:
        return jsonify({"message": "يرجى إدخال رقم الكارت أو المشترك"}), 400

    audit_logs.insert
