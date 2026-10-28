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

@app.route('/api/pay', methods=['POST'])
def process_payment():
    data = request.json or {}
    card_id = data.get('card_number')
    months = data.get('months')
    price = data.get('price')
    agent = data.get('agent', 'unknown')

    if not card_id or not months or not price:
        return jsonify({"message": "بيانات التسديد غير مكتملة"}), 400

    price_table = {2: 3000, 3: 4500, 4: 6000, 6: 8000, 12: 15000}
    
    if int(months) in price_table and int(price) != price_table[int(months)]:
        return jsonify({"message": "خطأ في مطابقة السعر المحدد للباقة"}), 400

    cards_cloud_db[card_id] = {
        "subscriber_name": f"مشترك رقم {card_id}",
        "status": "Active subscriber",
        "package": f"باقة {months} أشهر",
        "expiry_date": f"تم التمديد لمدة {months} أشهر"
    }

    audit_logs.insert(0, {
        "action": "تسديد اشتراك", 
        "card": card_id, 
        "months": months, 
        "price": price, 
        "agent": agent
    })

    return jsonify({
        "message": f"تمت عملية التسديد بنجاح لمدة {months} أشهر بمبلغ {price} ريال وتحديث النظام السحابي",
        "card_number": card_id,
        "paid_amount": price
    }), 200

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify({"logs": audit_logs[:30]}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
