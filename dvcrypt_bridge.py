import datetime
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

DVCrypt_EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Subscriber - DVCrypt</title>
    <style>
        * { box-sizing: border-box; font-family: Tahoma, sans-serif; }
        body { background-color: #262626; color: #000; margin: 0; padding: 10px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .win-box { background: #f0f0f0; border: 1px solid #7a7a7a; border-radius: 3px; width: 100%; max-width: 460px; padding: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.7); }
        .win-header { background: linear-gradient(to bottom, #10336b, #0c2347); color: white; padding: 6px 10px; font-weight: bold; font-size: 0.9rem; display: flex; justify-content: space-between; align-items: center; margin: -12px -12px 12px -12px; }
        .form-row { margin-bottom: 8px; display: flex; align-items: center; }
        .form-row label { width: 100px; font-size: 0.8rem; font-weight: bold; color: #000; }
        .form-row input, .form-row select { flex: 1; padding: 5px; border: 1px solid #7f9db9; background: #fff; font-size: 0.9rem; border-radius: 2px; }
        .section-box { border: 1px solid #ccc; padding: 10px; margin-top: 10px; background: #fafafa; }
        .status-group { font-size: 0.85rem; margin-top: 5px; }
        .status-group label { display: block; margin-bottom: 4px; font-weight: normal; }
        .btn-row { display: flex; justify-content: flex-end; gap: 6px; margin-top: 12px; }
        .win-btn { background: #e1e1e1; border: 1px solid #adadad; padding: 5px 15px; font-size: 0.85rem; cursor: pointer; border-radius: 2px; font-weight: bold; min-width: 75px; }
        .win-btn:hover { background: #e5f1fb; border-color: #0078d7; }
        .win-btn.ok { background: #10b981; color: white; border-color: #059669; }
        .win-btn.ok:hover { background: #059669; }
        .msg { text-align: center; font-size: 0.85rem; margin-top: 5px; font-weight: bold; }
    </style>
</head>
<body>

<div class="win-box">
    <div class="win-header"><span>Edit subscriber</span><span>✕</span></div>
    
    <!-- بحث عن المشترك برقم الكارت أولاً -->
    <div class="form-row">
        <label>Subscriber ID:</label>
        <input type="text" id="subId" placeholder="أدخل رقم الكارت (مثال: 00025)..." style="background:#fff;">
        <button class="win-btn" onclick="searchSubscriber()" style="margin-right:5px;">بحث</button>
    </div>

    <div class="form-row">
        <label>Name:</label>
        <input type="text" id="subName" readonly style="background:#e9ecef; color:#0d6efd; font-weight:bold;">
    </div>
    <div class="form-row">
        <label>Address:</label>
        <input type="text" id="subAddress" readonly style="background:#e9ecef;">
    </div>
    <div class="form-row">
        <label>Phone:</label>
        <input type="text" id="subPhone" readonly style="background:#e9ecef;">
    </div>

    <div class="section-box">
        <div style="font-weight:bold; font-size:0.85rem; margin-bottom:6px; color:#333;">Subscription & Payment</div>
        
        <div class="form-row">
            <label>سعر الباقة:</label>
            <select id="priceSelect" onchange="calculateExpiry()">
                <option value="3000">3000 ريال (شهرين)</option>
                <option value="4500">4500 ريال (ثلاثة أشهر)</option>
                <option value="6000">6000 ريال (أربعة أشهر)</option>
                <option value="8000">8000 ريال (نصف سنة)</option>
                <option value="15000">15000 ريال (سنة كاملة)</option>
            </select>
        </div>

        <div class="form-row">
            <label>Paid untill:</label>
            <input type="text" id="paidUntil" readonly style="background:#e9ecef; font-weight:bold; color:#d9534f;">
        </div>

        <div class="status-group">
            <label><input type="radio" name="status" checked> Active subscriber</label>
            <label><input type="radio" name="status"> Not used</label>
            <label><input type="radio" name="status"> Activated by administrator</label>
        </div>
    </div>

    <div class="msg" id="actionMsg"></div>

    <div class="btn-row">
        <button class="win-btn ok" onclick="savePayment()">OK</button>
        <button class="win-btn" onclick="location.reload()">Cancel</button>
    </div>
</div>

<script>
    function searchSubscriber() {
        const id = document.getElementById('subId').value;
        if(!id) { alert("الرجاء إدخال رقم الكارت"); return; }

        fetch(`/api/get-subscriber?id=${id}`)
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                document.getElementById('subName').value = data.name;
                document.getElementById('subAddress').value = data.address || '';
                document.getElementById('subPhone').value = data.phone || '';
                calculateExpiry();
            } else {
                alert("لم يتم العثور على المشترك");
            }
        });
    }

    function calculateExpiry() {
        const price = document.getElementById('priceSelect').value;
        let months = 2;
        if(price === '4500') months = 3;
        if(price === '6000') months = 4;
        if(price === '8000') months = 6;
        if(price === '15000') months = 12;

        let date = new Date();
        date.setMonth(date.getMonth() + months);
        
        // تنسيق التاريخ DD/MM/YYYY مطابق لبرنامج DVCrypt
        let dd = String(date.getDate()).padStart(2, '0');
        let mm = String(date.getMonth() + 1).padStart(2, '0');
        let yyyy = date.getFullYear();
        
        document.getElementById('paidUntil').value = `${dd}/${mm}/${yyyy}`;
    }

    function savePayment() {
        const id = document.getElementById('subId').value;
        const price = document.getElementById('priceSelect').value;
        const expiry = document.getElementById('paidUntil').value;
        const msg = document.getElementById('actionMsg');

        if(!id) { alert("اختر الكارت أولاً"); return; }

        msg.innerHTML = "<span style='color:#0284c7'>جاري إرسال التسديد وتحديث التاريخ...</span>";

        fetch('/api/save-payment', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id: id, price: price, expiry: expiry })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                msg.innerHTML = "<span style='color:#10b981;'>✓ تم التسديد وتحديث تاريخ الانتهاء بنجاح!</span>";
            } else {
                msg.innerHTML = "<span style='color:#d9534f;'>فشلت عملية التسديد</span>";
            }
        });
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DVCrypt_EDIT_TEMPLATE)

@app.route('/api/get-subscriber', methods=['GET'])
def get_sub():
    sub_id = request.args.get('id')
    try:
        # استدعاء البيانات من الكمبيوتر المحلي عبر Tailscale
        r = requests.get(f"http://100.87.45.65:8100/api/subscriber", params={"id": sub_id}, timeout=3)
        return jsonify(r.json())
    except:
        # رد افتراضي للتجربة في حال لم يتم تشغيل سيرفر المحل بعد
        return jsonify({
            "status": "success",
            "name": "احمد علي حسين العيدروس",
            "address": "سيئون - المحل الرئيسي",
            "phone": "+967771948540"
        })

@app.route('/api/save-payment', methods=['POST'])
def save_pay():
    data = request.json
    try:
        r = requests.post(f"http://100.87.45.65:8100/api/pay", json=data, timeout=3)
        return jsonify(r.json())
    except:
        return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
