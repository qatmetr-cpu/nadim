from flask import Flask, render_template_string, request, jsonify
import socket

app = Flask(__name__)

CONFIG = {
    "PC_IP": "192.168.0.160",
    "PC_PORT": 8100,
    "TAILSCALE_DOMAIN": "sssd.talaf.82e5.ts.net",
    "TAILSCALE_PORT": 8101
}

# قائمة الحسابات مطابقة لبرنامج الكمبيوتر تماماً
USERS = [
    {"id": "admin", "name": "Administrator", "icon": "👑"},
    {"id": "operator", "name": "Operator", "icon": "⚙️"},
    {"id": "info", "name": "Information", "icon": "ℹ️"},
    {"id": "Anwer", "name": "Anwer", "icon": "👤"},
    {"id": "nadeem", "name": "nadeem", "icon": "👤"},
    {"id": "mohamedahmed", "name": "Mohamed Ahmed", "icon": "👤"},
    {"id": "mohammedsaleh", "name": "mohammed saleh", "icon": "👤"},
    {"id": "abas", "name": "abas alhamed", "icon": "👤"},
    {"id": "Majed", "name": "Majed", "icon": "👤"},
    {"id": "zakariya", "name": "zakariya", "icon": "👤"}
]

SUBSCRIBERS = [
    {"sub_id": "000001", "name": "محمد صالح بن الشيخ أبوبكر", "address": "عاقل بالشبكة", "phone": "771721130", "status": "Subscription ended"},
    {"sub_id": "000002", "name": "محمد سالم عبدالله حسان", "address": "العميده", "phone": "770266215", "status": "Subscription ended"},
    {"sub_id": "000025", "name": "احمد علي حسين العيدروس", "address": "مريمه", "phone": "775464311", "status": "Active subscriber"},
    {"sub_id": "000031", "name": "عبدالكريم كرامة التميمي", "address": "الغرفة", "phone": "778436285", "status": "Subscription ended"}
]

# قالب الواجهة مطابق لبرنامج الكمبيوتر
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Client - Subscribers</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #dcdde1; margin: 0; padding: 0; color: #000; }
        .top-bar { background: #e74c3c; color: white; padding: 6px; text-align: center; font-size: 13px; font-weight: bold; }
        .menu-bar { background: #f5f6fa; border-bottom: 1px solid #bdc3c7; padding: 4px 10px; font-size: 12px; display: flex; gap: 15px; }
        
        /* نافذة تسجيل الدخول الشبيهة بالكمبيوتر */
        .win-window { width: 95%; max-width: 420px; background: #eceff1; border: 1px solid #90a4ae; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin: 40px auto; border-radius: 3px; }
        .win-header { background: linear-gradient(to bottom, #cfd8dc, #b0bec5); padding: 5px 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #90a4ae; display: flex; justify-content: space-between; align-items: center; }
        .win-body { padding: 15px; }
        
        /* قائمة الحسابات مثل ويندوز */
        .account-box { border: 1px solid #78909c; background: white; height: 160px; overflow-y: scroll; margin-bottom: 10px; }
        .account-item { padding: 4px 8px; font-size: 13px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .account-item:hover, .account-item.selected { background: #0078d7; color: white; }
        
        input[type="password"] { width: 100%; padding: 5px; border: 1px solid #78909c; box-sizing: border-box; margin-bottom: 10px; }
        .win-btn { background: #e0e0e0; border: 1px solid #78909c; padding: 4px 15px; font-size: 13px; cursor: pointer; float: right; border-radius: 2px; }
        .win-btn:hover { background: #d0d0d0; }

        /* شاشة جدول المشتركين */
        #dashboard { display: none; padding: 5px; }
        table { width: 100%; border-collapse: collapse; background: white; font-size: 11px; }
        th, td { border: 1px solid #dcdde1; padding: 4px 6px; text-align: left; }
        th { background: #f1f2f6; font-weight: bold; }
        .status-active { color: #27ae60; font-weight: bold; }
        .status-ended { color: #c0392b; }
        .toolbar { background: #f5f6fa; padding: 5px; border: 1px solid #bdc3c7; margin-bottom: 5px; font-size: 12px; }
    </style>
</head>
<body>

    <div class="top-bar">Free license (non-professional use).</div>
    <div class="menu-bar">
        <span><b>Main</b></span>
        <span><b>View</b></span>
        <span><b>?</b></span>
        <span style="margin-left:auto; color: #555;">Server IP: {{ config.PC_IP }}:{{ config.PC_PORT }}</span>
    </div>

    <!-- نافذة تسجيل الدخول (مطابقة للصورة الأولى) -->
    <div id="login-window" class="win-window">
        <div class="win-header">
            <span>Login</span>
            <span>✕</span>
        </div>
        <div class="win-body">
            <div style="font-size: 12px; margin-bottom: 4px;">Account</div>
            <div class="account-box" id="account-list">
                {% for u in users %}
                <div class="account-item {% if loop.first %}selected{% endif %}" onclick="selectUser('{{ u.id }}', this)">
                    <span>{{ u.icon }}</span> <b>{{ u.id }}</b> <span style="color: #555; margin-left: auto;">{{ u.name }}</span>
                </div>
                {% endfor %}
            </div>
            
            <div style="font-size: 12px; margin-bottom: 4px;">Password</div>
            <input type="password" id="password" placeholder="أدخل كلمة المرور...">
            
            <div style="overflow: hidden;">
                <button class="win-btn" onclick="doLogin()">Login</button>
            </div>
        </div>
    </div>

    <!-- واجهة النظام وجدول المشتركين (مطابقة للصورة الثانية) -->
    <div id="dashboard">
        <div class="toolbar">
            <span>🗂️ <b>DVCrypt Client - Subscribers</b></span>
            <button onclick="doLogout()" style="float:left; font-size:11px; padding:2px 8px;">Logout</button>
        </div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Subscriber ID</th>
                        <th>Name</th>
                        <th>Address</th>
                        <th>Phone</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for sub in subscribers %}
                    <tr>
                        <td><b>{{ sub.sub_id }}</b></td>
                        <td>{{ sub.name }}</td>
                        <td>{{ sub.address }}</td>
                        <td>{{ sub.phone }}</td>
                        <td><span class="{{ 'status-active' if 'Active' in sub.status else 'status-ended' }}">{{ sub.status }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let selectedUser = 'admin';
        function selectUser(userId, element) {
            document.querySelectorAll('.account-item').forEach(el => el.classList.remove('selected'));
            element.classList.add('selected');
            selectedUser = userId;
        }

        function doLogin() {
            let pass = document.getElementById('password').value;
            // الدخول المباشر وعرض واجهة البرنامج تماماً مثل الكمبيوتر
            document.getElementById('login-window').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
        }

        function doLogout() {
            document.getElementById('login-window').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, config=CONFIG, users=USERS, subscribers=SUBSCRIBERS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8101)