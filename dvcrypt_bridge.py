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

# الواجهة الكاملة والشاملة (تتضمن لوحة الإدارة، الوكلاء، جدول الأسعار، والتسديد)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة شبكة ALSAFA TV</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 15px; text-align: center; }
        .container { max-width: 600px; margin: 20px auto; background: #1e293b; padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #334155; font-size: 15px; box-sizing: border-box; background: #0f172a; color: #fff; }
        button { background: #0ea5e9; color: #fff; font-weight: bold; cursor: pointer; border: none; }
        button:hover { background: #0284c7; }
        .card-box { background: #334155; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: right; }
        .price-table { width: 100%; margin-top: 15px; border-collapse: collapse; font-size: 14px; }
        .price-table th, .price-table td { border: 1px solid #475569; padding: 8px; text-align: center; }
        .price-table th { background: #0f172a; }
        .status { margin-top: 15px; color: #22c55e; font-weight: bold; font-size: 14px; }
        .admin-section { background: #1e293b; border: 1px dashed #0ea5e9; padding: 15px; margin-top: 20px; border-radius: 8px; text-align: right; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🌐 نظام إدارة شبكة ALSAFA TV</h2>
        
        <!-- قسم تسجيل الدخول -->
        <div id="login-section">
            <p>يرجى تسجيل الدخول للبدء</p>
            <input type="text" id="username" placeholder="اسم المستخدم" value="Nadim">
            <input type="password" id="password" placeholder="كلمة المرور" value="ofsad">
            <button onclick="login()">دخول للنظام</button>
        </div>

        <!-- لوحة التحكم الرئيسية (مخفية حتى يتم تسجيل الدخول) -->
        <div id="dashboard" style="display:none;">
            <h3 id="welcome-msg" style="color: #38bdf8;"></h3>
            
            <hr style="border-color: #334155; margin: 20px 0;">
            
            <h4>🔍 الاستعلام عن كارت / مشترك</h4>
            <input type="text" id="card-id" placeholder="أدخل رقم الكارت أو المشترك">
            <button onclick="searchCard()">بحث عن الكارت</button>
            <div id="search-result" class="card-box" style="display:none;"></div>

            <!-- نافذة التسديد والتمديد -->
            <div id="payment-box" style="display:none; margin-top: 20px; background: #0f172a; padding: 15px; border-radius: 8px; text-align: right;">
                <h4 style="color: #38bdf8; text-align: center;">💳 نافذة تسديد اشتراك</h4>
                <label>اختر الباقة والمدة:</label>
                <select id="pay-months" onchange="updatePrice()">
                    <option value="2">باقة شهرين - 3000 ريال</option>
                    <option value="3">باقة 3 أشهر - 4500 ريال</option>
                    <option value="4">باقة 4 أشهر - 6000 ريال</option>
                    <option value="6">باقة 6 أشهر - 8000 ريال</option>
                    <option value="12">باقة سنة (12 شهر) - 15000 ريال</option>
                </select>
                <input type="number" id="pay-price" value="3000" placeholder="المبلغ المطلوب">
                <button onclick="processPayment()">تنفيذ وتأكيد التسديد</button>
            </div>

            <!-- جدول الأسعار المعتمد -->
            <div style="margin-top: 25px; text-align: right;">
                <h4 style="color: #cbd5e1;">📋 جدول أسعار باقات نت هوم و ALSAFA TV:</h4>
                <table class="price-table">
                    <tr><th>المدة</th><th>السعر الرسمي</th></tr>
                    <tr><td>شهرين</td><td>3000 ريال</td></tr>
                    <tr><td>3 أشهر</td><td>4500 ريال</td></tr>
                    <tr><td>4 أشهر</td><td>6000 ريال</td></tr>
                    <tr><td>6 أشهر</td><td>8000 ريال</td></tr>
                    <tr><td>سنة كاملة</td><td>15000 ريال</td></tr>
                </table>
            </div>

            <!-- لوحة تحكم المسؤول لإضافة الوكلاء -->
            <div id="admin-panel" class="admin-section" style="display:none;">
                <h4 style="color: #f43f5e;">🛠️ لوحة المسؤول (إدارة الوكلاء)</h4>
                <input type="text" id="new-agent-name" placeholder="اسم الوكيل الجديد">
                <input type="password" id="new-agent-pass" placeholder="كلمة مرور الوكيل الجديد">
                <button onclick="addAgent()" style="background: #f43f5e;">إضافة وكيل جديد</button>
            </div>
        </div>

        <p class="status">السيرفر السحابي متصل بنجاح 🟢</p>
    </div>

    <script>
        let currentUser = "";
        let isAdmin = false;

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
                isAdmin = data.is_admin;
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('welcome-msg').innerText = "مرحباً بك: " + u;
                if(isAdmin) {
                    document.getElementById('admin-panel').style.display = 'block';
                }
            } else {
                alert(data.message);
            }
        }

        async function searchCard() {
            const card = document.getElementById('card-id').value;
            if(!card) return alert('يرجى إدخال رقم الكارت');
            const res = await fetch(`/api/search?card=${card}&agent=${currentUser}`);
            const data = await res.json();
            
            const resBox = document.getElementById('search-result');
            resBox.style.display = 'block';
            resBox.innerHTML = `
                <b>رقم الكارت:</b> ${data.card_number}<br>
                <b>اسم المشترك:</b> ${data.subscriber_name}<br>
                <b>الحالة:</b> ${data.status}<br>
                <b>الباقة الحالية:</b> ${data.package}<br>
                <b>الانتهاء:</b> ${data.expiry_date}
            `;
            document.getElementById('payment-box').style.display = 'block';
        }

        function updatePrice() {
            const months = document.getElementById('pay-months').value;
            const prices = {2: 3000, 3: 4500, 4: 6000, 6: 8000, 12: 15000};
            document.getElementById('pay-price').value = prices[months];
        }

        async function processPayment() {
            const card = document.getElementById('card-id').value;
            const months = document.getElementById('pay-months').value;
            const price = document.getElementById('pay-price').value;

            const res = await fetch('/api/pay', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({card_number: card, months: months, price: price, agent: currentUser})
            });
            const data = await res.json();
            alert(data.message);
            if(res.ok) searchCard();
        }

        async function addAgent() {
            const name = document.getElementById('new-agent-name').value;
            const pass = document.getElementById('new-agent-pass').value;
            const res = await fetch('/api/add-agent', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({admin_user: currentUser, new_username: name, new_password: pass})
            });
            const data = await res.json();
            alert(data.message);
            if(res.ok) {
                document.getElementById('new-agent-name').value = '';
                document.getElementById('new-agent-pass').value = '';
            }
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

@app.route('/api/add-agent', methods=['POST'])
def add_agent():
    data = request.json or {}
    admin_user = data.get('admin_user')
    new_name = data.get('new_username')
    new_pass = data.get('new_password')

    if admin_user != ADMIN_USER:
        return jsonify({"message": "غير مسموح إلا للمسؤول الرئيسي"}), 403

    if not new_name or not new_pass:
        return jsonify({"message": "يرجى إدخال البيانات كاملة"}), 400

    agents_db[new_name] = new_pass
    return jsonify({"message": f"تم إضافة الوكيل {new_name} بنجاح"}), 200

@app.route('/api/search', methods=['GET'])
def search_card():
    card_id = request.args.get('card')
    agent = request.args.get('agent', 'unknown')

    if not card_id:
        return jsonify({"message": "أدخل رقم الكارت"}), 400

    audit_logs.insert(0, {"action": "بحث", "card": card_id, "agent": agent})

    if card_id in cards_cloud_db:
        info = cards_cloud_db[card_id]
        return jsonify({
            "card_number": card_id,
            "subscriber_name": info["subscriber_name"],
            "status": info["status"],
            "package": info["package"],
            "expiry_date": info["expiry_date"]
        }), 200
    else:
        return jsonify({
            "card_number": card_id,
            "subscriber_name": f"مشترك جديد ({card_id})",
            "status": "Not used",
            "package": "غير محددة",
            "expiry_date": "متاح للتسديد"
        }), 200

@app.route('/api/pay', methods=['POST'])
def process_payment():
    data = request.json or {}
    card_id = data.get('card_number')
    months = data.get('months')
    price = data.get('price')
    agent = data.get('agent', 'unknown')

    if not card_id or not months or not price:
        return jsonify({"message": "بيانات غير مكتملة"}), 400

    cards_cloud_db[card_id] = {
        "subscriber_name": f"مشترك كارت {card_id}",
        "status": "Active",
        "package": f"باقة {months} أشهر",
        "expiry_date": f"تم التمديد بمعرفة الوكيل ({agent})"
    }

    audit_logs.insert(0, {"action": "تسديد", "card": card_id, "months": months, "price": price, "agent": agent})

    return jsonify({"message": f"تم تسديد مبلغ {price} ريال وتمديد الباقة بنجاح!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
