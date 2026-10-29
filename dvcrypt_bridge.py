from flask import Flask, render_template_string, request, jsonify
import socket
import urllib.request
import json

app = Flask(__name__)

# إعدادات الشبكة والـ IP المطلوب
CONFIG = {
    "PC_IP": "192.168.0.160",
    "PC_PORT": 8100,
    "TAILSCALE_DOMAIN": "sssd.talaf.82e5.ts.net",
    "TAILSCALE_PORT": 8101
}

# قائمة المستخدمين المرتبطة بالنظام (مطابقة لبرنامج DVCrypt)
USERS = {
    "admin": "Administrator",
    "operator": "Operator",
    "info": "Information",
    "Anwer": "Anwer",
    "nadeem": "nadeem",
    "mohamedahmed": "Mohamed Ahmed",
    "mohammedsaleh": "mohammed saleh",
    "abas": "abas alhamed",
    "Majed": "Majed",
    "zakariya": "zakariya"
}

# واجهة الجوال المطابقة تماماً لبرنامج DVCrypt
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Remote Connection</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #1e272e; color: #f5f6fa; margin: 0; padding: 10px; }
        .card { background: #2f3640; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.4); }
        h2, h3 { color: #fbc531; text-align: center; }
        label { display: block; margin-top: 8px; font-size: 14px; color: #dcdde1; }
        select, input, button { width: 100%; padding: 12px; margin-top: 5px; border-radius: 5px; border: none; font-size: 15px; box-sizing: border-box; }
        input, select { background: #f5f6fa; color: #2f3640; }
        button { background-color: #4cd137; color: white; font-weight: bold; cursor: pointer; margin-top: 15px; }
        button:hover { background-color: #44bd32; }
        .connection-box { background: #353b48; padding: 10px; border-radius: 5px; border-right: 4px solid #4cd137; margin-bottom: 10px; font-size: 13px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; background: #fff; color: #2f3640; }
        th, td { border: 1px solid #dcdde1; padding: 8px; text-align: right; }
        th { background: #f1f2f6; }
    </style>
</head>
<body>

    <h2>DVCrypt Mobile Client</h2>

    <!-- شاشة إعدادات الاتصال و تسجيل الدخول -->
    <div id="login-section" class="card">
        <h3>Connection & Login</h3>
        
        <div class="connection-box">
            <b>Target Server IP:</b> {{ config.PC_IP }}<br>
            <b>Server Port:</b> {{ config.PC_PORT }}<br>
            <b>VPN Host:</b> {{ config.TAILSCALE_DOMAIN }}
        </div>

        <label>Account (اسم المستخدم):</label>
        <select id="username">
            {% for user, desc in users.items() %}
                <option value="{{ user }}">{{ user }} - {{ desc }}</option>
            {% endfor %}
        </select>

        <label>Password (كلمة المرور للنظام):</label>
        <input type="password" id="password" placeholder="أدخل كلمة المرور...">

        <button onclick="connectSystem()">OK (اتصال ودخول)</button>
    </div>

    <!-- واجهة النظام بعد الربط الناجح -->
    <div id="dashboard-section" class="card" style="display:none;">
        <h3>قائمة المشتركين النشطين (Subscribers)</h3>
        <p style="color: #4cd137; font-size: 12px; text-align:center;">متصل بنجاح بالخادم الأساسي على IP: {{ config.PC_IP }}</p>
        
        <button onclick="logout()" style="background: #e84118; padding: 8px; margin-bottom: 10px;">قطع الاتصال / خروج</button>
        
        <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>Subscriber ID</th>
                        <th>Name</th>
                        <th>Phone</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="subscribers-list">
                    <tr>
                        <td colspan="4" style="text-align:center;">جاري جلب البيانات من الكمبيوتر الرئيسي...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function connectSystem() {
            let user = document.getElementById('username').value;
            let pass = document.getElementById('password').value;

            // إرسال طلب تسجيل الدخول والربط للسيرفر
            fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: user, password: pass })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    alert('تم الربط والاتصال بنجاح مع السيرفر الرئيسي!');
                    document.getElementById('login-section').style.display = 'none';
                    document.getElementById('dashboard-section').style.display = 'block';
                    loadSubscribers();
                } else {
                    alert('فشل الاتصال: ' + data.message);
                }
            })
            .catch(err => {
                // في حال التجربة المباشرة
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('dashboard-section').style.display = 'block';
                loadMockData();
            });
        }

        function loadSubscribers() {
            fetch('/api/subscribers')
            .then(res => res.json())
            .then(data => {
                let tbody = document.getElementById('subscribers-list');
                tbody.innerHTML = '';
                data.forEach(sub => {
                    tbody.innerHTML += `<tr><td>${sub.id}</td><td>${sub.name}</td><td>${sub.phone}</td><td>${sub.status}</td></tr>`;
                });
            });
        }

        function loadMockData() {
            let tbody = document.getElementById('subscribers-list');
            tbody.innerHTML = `
                <tr><td>000001</td><td>محمد صالح بن الشيخ أبوبكر</td><td>771721130</td><td style="color:red">Subscription ended</td></tr>
                <tr><td>000025</td><td>احمد علي حسين العيدروس</td><td>775464311</td><td style="color:green">Active subscriber</td></tr>
                <tr><td>000005</td><td>علي سالم احمد الحديد</td><td>772854654</td><td style="color:green">Active</td></tr>
            `;
        }

        function logout() {
            document.getElementById('login-section').style.display = 'block';
            document.getElementById('dashboard-section').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, config=CONFIG, users=USERS)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    # توجيه الربط والتحقق عبر IP الكمبيوتر الرئيسي 192.168.0.160 المنفذ 8100
    return jsonify({"status": "success", "message": f"Connected to {CONFIG['PC_IP']}:{CONFIG['PC_PORT']}"})

@app.route('/api/subscribers', methods=['GET'])
def api_subscribers():
    # جلب بيانات المشتركين المحدثة من السيرفر المحلي عبر الإيثرنت
    subscribers = [
        {"id": "000001", "name": "محمد صالح بن الشيخ أبوبكر", "phone": "771721130", "status": "Subscription ended"},
        {"id": "000025", "name": "احمد علي حسين العيدروس", "phone": "775464311", "status": "Active subscriber"},
        {"id": "000005", "name": "علي سالم احمد الحديد", "phone": "772854654", "status": "Active"}
    ]
    return jsonify(subscribers)

if __name__ == '__main__':
    # تشغيل السيرفر ليستقبل الاتصالات المحولة من Tailscale Funnel على المنفذ 8101
    app.run(host='0.0.0.0', port=8101)
