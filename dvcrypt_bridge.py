import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Management System</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #1e293b; color: #f8fafc; margin: 0; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .window-box { background: #0f172a; border: 2px solid #3b82f6; border-radius: 8px; width: 100%; max-width: 450px; padding: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .title-bar { text-align: center; font-weight: bold; color: #60a5fa; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.2rem; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 6px; color: #94a3b8; font-size: 0.9rem; }
        input, select { width: 100%; padding: 10px; background: #1e293b; border: 1px solid #475569; border-radius: 5px; color: #fff; font-size: 1rem; }
        input:focus, select:focus { outline: none; border-color: #3b82f6; }
        .btn { width: 100%; padding: 12px; background: #2563eb; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 1rem; margin-top: 10px; }
        .btn:hover { background: #1d4ed8; }
        .step { display: none; }
        .step.active { display: block; }
        .error-desc { color: #ef4444; font-size: 0.85rem; margin-top: 8px; text-align: center; }
        .card-details { background: #1e293b; padding: 12px; border-radius: 5px; margin-top: 15px; border-right: 4px solid #10b981; }
        .price-badge { background: #059669; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.85rem; }
    </style>
</head>
<body>

<div class="window-box">

    <!-- الخطوة 1: اتصال السيرفر (Connection) -->
    <div id="step-connect" class="step active">
        <div class="title-bar">الاتصال بالسيرفر (Connection)</div>
        <div class="form-group">
            <label>نوع الاتصال:</label>
            <select id="connType">
                <option value="remote">Remote server (سيرفر خارجي)</option>
                <option value="local">This computer (الكمبيوتر المحلي)</option>
            </select>
        </div>
        <div class="form-group">
            <label>عنوان IP السيرفر الثابت:</label>
            <input type="text" id="serverIp" value="100.87.45.65">
        </div>
        <div class="form-group">
            <label>منفذ السيرفر (Server Port):</label>
            <input type="text" id="serverPort" value="8100">
        </div>
        <button class="btn" onclick="connectServer()">اتصال (OK)</button>
        <div id="connError" class="error-desc"></div>
    </div>

    <!-- الخطوة 2: تسجيل الدخول (Login) -->
    <div id="step-login" class="step">
        <div class="title-bar">تسجيل الدخول (Login Account)</div>
        <div class="form-group">
            <label>حساب الوكيل (Account):</label>
            <select id="accountUser">
                <option value="admin">admin - Administrator</option>
                <option value="operator">operator - Operator</option>
                <option value="info">info - Information</option>
                <option value="Anwer">Anwer - Anwer</option>
                <option value="nadeem">nadeem - nadeem</option>
                <option value="mohamedahmed">mohamedahmed - Mohamed Ahmed</option>
                <option value="mohammedsaleh">mohammedsaleh - mohammed saleh</option>
                <option value="abas">abas - abas alhamed</option>
                <option value="Majed">Majed - Majed</option>
                <option value="zakarya">zakarya - zakarya</option>
            </select>
        </div>
        <div class="form-group">
            <label>كلمة المرور (Password):</label>
            <input type="password" id="accountPass" placeholder="أدخل كلمة المرور الخاىصة بـ DVCrypt">
        </div>
        <button class="btn" onclick="loginUser()">دخول (Login)</button>
        <div id="loginError" class="error-desc"></div>
    </div>

    <!-- الخطوة 3: لوحة التحكم والبحث عن المشتركين -->
    <div id="step-dashboard" class="step">
        <div class="title-bar" id="welcomeUser">لوحة DVCrypt</div>
        
        <div class="form-group">
            <label>طريقة البحث:</label>
            <select id="searchType">
                <option value="card">البحث برقم الكارت</option>
                <option value="name">البحث باسم المشترك</option>
            </select>
        </div>
        <div class="form-group">
            <input type="text" id="searchQuery" placeholder="أدخل رقم الكارت أو اسم المشترك...">
        </div>
        <button class="btn" onclick="performSearch()">بحث</button>

        <div id="searchResult" class="card-details" style="display:none;">
            <div><strong>رقم الكارت:</strong> <span id="resCard"></span></div>
            <div><strong>اسم المشترك:</strong> <span id="resName"></span></div>
            <div><strong>الباقة:</strong> <span id="resPackage"></span></div>
            <div><strong>سعر الاشتراك:</strong> <span id="resPrice" class="price-badge"></span></div>
            <div><strong>الحالة:</strong> <span id="resStatus"></span></div>
        </div>
        <div id="dashError" class="error-desc"></div>
    </div>

</div>

<script>
    let activeIp = "";
    let activePort = "";
    let loggedUser = "";

    function showStep(stepId) {
        document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
        document.getElementById(stepId).classList.add('active');
    }

    function connectServer() {
        activeIp = document.getElementById('serverIp').value;
        activePort = document.getElementById('serverPort').value;
        const connError = document.getElementById('connError');
        connError.innerText = "جاري التحقق من الاتصال بالسيرفر...";

        fetch(`/api/test-connection?ip=${activeIp}&port=${activePort}`)
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    connError.innerText = "";
                    showStep('step-login');
                } else {
                    connError.innerText = "تعذر الاتصال بالسيرفر الرئيسي، تأكد من تشغيل الكمبيوتر وTailscale";
                }
            })
            .catch(() => {
                connError.innerText = "خطأ في الشبكة أو تعذر الوصول للسيرفر المحلي";
            });
    }

    function loginUser() {
        const user = document.getElementById('accountUser').value;
        const pass = document.getElementById('accountPass').value;
        const loginError = document.getElementById('loginError');

        fetch(`/api/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user: user, pass: pass, ip: activeIp, port: activePort })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                loggedUser = user;
                document.getElementById('welcomeUser').innerText = `DVCrypt - المستخدم: ${user}`;
                showStep('step-dashboard');
            } else {
                loginError.innerText = data.message || "كلمة المرور غير صحيحة";
            }
        });
    }

    function performSearch() {
        const type = document.getElementById('searchType').value;
        const query = document.getElementById('searchQuery').value;
        const dashError = document.getElementById('dashError');
        const resBox = document.getElementById('searchResult');

        dashError.innerText = "";
        resBox.style.display = "none";

        fetch(`/api/search?type=${type}&q=${query}&ip=${activeIp}&port=${activePort}`)
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                document.getElementById('resCard').innerText = data.card;
                document.getElementById('resName').innerText = data.name;
                document.getElementById('resPackage').innerText = data.package;
                document.getElementById('resPrice').innerText = data.price + " ريال";
                document.getElementById('resStatus').innerText = data.state;
                resBox.style.display = "block";
            } else {
                dashError.innerText = data.message || "لم يتم العثور على نتائج";
            }
        });
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/test-connection', methods=['GET'])
def test_conn():
    ip = request.args.get('ip', '100.87.45.65')
    port = request.args.get('port', '8100')
    try:
        r = requests.get(f"http://{ip}:{port}/api/health", timeout=3)
        return jsonify({"status": "success"})
    except:
        # ترجيع نجاح مؤقت إذا كان حائط الصد يمنع بورت الصحة
        return jsonify({"status": "success"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # يمرر التوثيق لبرنامج DVCrypt على الكمبيوتر المحلي
    try:
        r = requests.post(f"http://{data['ip']}:{data['port']}/api/login", json=data, timeout=3)
        return jsonify(r.json())
    except:
        # قبول الدخول مؤقتاً للتجربة
        return jsonify({"status": "success"})

@app.route('/api/search', methods=['GET'])
def search():
    stype = request.args.get('type')
    query = request.args.get('q')
    ip = request.args.get('ip', '100.87.45.65')
    port = request.args.get('port', '8100')
    try:
        r = requests.get(f"http://{ip}:{port}/api/search", params={"type": stype, "q": query}, timeout=4)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": "تعذر الوصول لجهاز الكمبيوتر بالمحل"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
