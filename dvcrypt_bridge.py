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

# واجهة الموقع مباشرة داخل الكود لتجنب أي مشاكل في مسار الملفات
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة ALSAFA TV</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #121212; color: #fff; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 500px; margin: 50px auto; background: #1e1e1e; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        input, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: none; font-size: 16px; box-sizing: border-box; }
        input { background: #2c2c2c; color: #fff; }
        button { background: #00bcd4; color: #fff; font-weight: bold; cursor: pointer; }
        button:hover { background: #0097a7; }
        .status { margin-top: 15px; color: #4caf50; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>نظام إدارة ALSAFA TV السحابي</h2>
        <div id="login-section">
            <input type="text" id="username" placeholder="اسم المستخدم">
            <input type="password" id="password" placeholder="كلمة المرور">
            <button onclick="login()">تسجيل الدخول</button>
        </div>
        <div id="dashboard" style="display:none;">
            <h3 id="welcome-msg"></h3>
            <input type="text" id="card-id" placeholder="أدخل رقم الكارت أو المشترك">
            <button onclick="searchCard()">بحث عن الكارت</button>
            <div id="result" style="margin-top:20px; text-align:right; background:#2c2c2c; padding:15px; border-radius:6px;"></div>
        </div>
        <p class="status">السيرفر متصل بنجاح 🟢</p>
    </div>

    <script>
        let currentUser = "";
        async function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            const res = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if(res.ok) {
                currentUser = u;
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('welcome-msg').innerText = "مرحباً بك، " + u;
            } else {
                alert(data.message);
            }
        }

        async function searchCard() {
            const card = document.getElementById('card-id').value;
            if(!card) return alert('يرجى إدخال رقم الكارت');
            const res = await fetch(`/api/search?card=${card}&agent=${currentUser}`);
            const data = await res.json();
            document.getElementById('result').innerHTML = `
                <b>اسم المشترك:</b> ${data.subscriber_name}<br>
                <b>الحالة:</b> ${data.status}<br>
                <b>الباقة:</b> ${data.package}<br>
                <b>تاريخ الانتهاء:</b> ${data.expiry_date}
            `;
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return HTML_CONTENT, 200

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

@app.route('/api/search', methods=['GET'])
def search_card():
    card_id = request.args.get('card')
    agent = request.args.get('agent', 'unknown')

    if not card_id:
        return jsonify({"message": "يرجى إدخال رقم الكارت أو المشترك"}), 400

    audit_logs.insert(0, {"action": "بحث عن كارت", "card": card_id, "agent": agent})

    if card_id in cards_cloud_db:
        card_info = cards_cloud_db[card_id]
        return jsonify({
            "card_number": card_id,
            "subscriber_name": card_info["subscriber_name"],
            "status": card_info["status"],
            "package": card_info["package"],
            "expiry_date": card_info["expiry_date"]
        }), 200
    else:
        return jsonify({
            "card_number": card_id,
            "subscriber_name": f"مشترك جديد ({card_id})",
            "status": "Not used",
            "package": "غير محددة",
            "expiry_date": "متاح للشحن والتسديد"
        }), 200

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify({"logs": audit_logs[:30]}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
