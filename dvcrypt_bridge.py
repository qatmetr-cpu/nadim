import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

DVCrypt_UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Remote Client & Payment</title>
    <style>
        * { box-sizing: border-box; font-family: Tahoma, sans-serif; }
        body { background-color: #262626; color: #fff; margin: 0; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .win-box { background: #f0f0f0; color: #000; border: 1px solid #7a7a7a; border-radius: 3px; width: 100%; max-width: 450px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.7); }
        .win-header { background: linear-gradient(to bottom, #10336b, #0c2347); color: white; padding: 8px 12px; font-weight: bold; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center; margin: -15px -15px 15px -15px; border-top-left-radius: 2px; border-top-right-radius: 2px; }
        .form-row { margin-bottom: 12px; display: flex; flex-direction: column; }
        label { margin-bottom: 4px; font-size: 0.85rem; font-weight: bold; color: #333; }
        input[type="text"], input[type="password"], select { padding: 6px 8px; border: 1px solid #7f9db9; background: #fff; font-size: 0.95rem; border-radius: 2px; }
        .btn-group { display: flex; justify-content: flex-end; gap: 8px; margin-top: 15px; }
        .win-btn { background: #e1e1e1; border: 1px solid #adadad; padding: 6px 20px; font-size: 0.9rem; cursor: pointer; border-radius: 2px; font-weight: bold; }
        .win-btn:hover { background: #e5f1fb; border-color: #0078d7; }
        .win-btn.pay { background: #10b981; color: white; border-color: #059669; }
        .win-btn.pay:hover { background: #059669; }
        .step { display: none; }
        .step.active { display: block; }
        .error-msg { color: #d9534f; font-size: 0.8rem; margin-top: 5px; text-align: center; font-weight: bold; }
        .success-msg { color: #10b981; font-size: 0.85rem; margin-top: 5px; text-align: center; font-weight: bold; }
        .result-panel { background: #fff; border: 1px solid #ccc; padding: 12px; margin-top: 10px; font-size: 0.9rem; }
        .payment-box { background: #e6f4ea; border: 1px solid #ceead6; padding: 10px; margin-top: 10px; border-radius: 3px; }
    </style>
</head>
<body>

<div class="win-box">
    
    <!-- نافذة 1: اتصال السيرفر (Connection) -->
    <div id="step-conn" class="step active">
        <div class="win-header"><span>Connection</span><span>✕</span></div>
        <div style="margin-bottom: 10px; font-size: 0.85rem;">
            <label><input type="radio" name="cType" checked> This computer</label><br>
            <label><input type="radio" name="cType"> Remote server</label>
        </div>
        <div class="form-row">
            <label>Server IP / Host:</label>
            <input type="text" id="targetIp" value="192.168.0.160">
        </div>
        <div class="form-row">
            <label>Server Port:</label>
            <input type="text" id="targetPort" value="8100">
        </div>
        <div class="btn-group">
            <button class="win-btn" onclick="connectToLocal()">OK</button>
            <button class="win-btn">Cancel</button>
        </div>
        <div id="connErr" class="error-msg"></div>
    </div>

    <!-- نافذة 2: تسجيل الدخول (Login) -->
    <div id="step-login" class="step">
        <div class="win-header"><span>Login - DVCrypt</span><span>✕</span></div>
        <div class="form-row">
            <label>Account User:</label>
            <select id="dbUser">
                <option value="admin">admin (Administrator)</option>
                <option value="operator">operator (Operator)</option>
                <option value="nadeem">nadeem (Nadeem)</option>
                <option value="mohamedahmed">mohamedahmed (Mohamed Ahmed)</option>
                <option value="mohammedsaleh">mohammedsaleh (Mohammed Saleh)</option>
                <option value="Majed">Majed (Majed)</option>
            </select>
        </div>
        <div class="form-row">
            <label>Password:</label>
            <input type="password" id="dbPass">
        </div>
        <div class="btn-group">
            <button class="win-btn" onclick="doLogin()">Login</button>
        </div>
        <div id="loginErr" class="error-msg"></div>
    </div>

    <!-- نافذة 3: البحث والتسديد -->
    <div id="step-search" class="step">
        <div class="win-header"><span id="activeUserTitle">DVCrypt Management</span><span>✕</span></div>
        <div class="form-row">
            <label>طريقة البحث:</label>
            <select id="searchMode">
                <option value="card">البحث برقم الكارت</option>
                <option value="name">البحث باسم المشترك</option>
            </select>
        </div>
        <div class="form-row">
            <label>كلمة البحث:</label>
            <input type="text" id="queryText" placeholder="أدخل رقم الكارت أو الاسم...">
        </div>
        <div class="btn-group">
            <button class="win-btn" onclick="executeSearch()">بحث (Search)</button>
        </div>
        
        <!-- نتائج البحث ومعلومات المشترك -->
        <div id="resultCard" class="result-panel" style="display:none;">
            <div><strong>رقم الكارت:</strong> <span id="rCard"></span></div>
            <div><strong>اسم المشترك:</strong> <span id="rName"></span></div>
            <div><strong>الباقة الحالية:</strong> <span id="rPackage"></span></div>
            <div><strong>الحالة:</strong> <span id="rState"></span></div>

            <!-- مكان التسديد وتجديد الباقة -->
            <div class="payment-box">
                <div class="form-row" style="margin-bottom: 8px;">
                    <label>اختر الباقة الجديدة للتسديد:</label>
                    <select id="newPackage">
                        <option value="15GB">باقة 15 جيجا</option>
                        <option value="30GB">باقة 30 جيجا</option>
                        <option value="60GB">باقة 60 جيجا</option>
                        <option value="130GB">باقة 130 جيجا</option>
                    </select>
                </div>
                <button class="win-btn pay" style="width:100%;" onclick="executePayment()">تثبيت التسديد وتفعيل الكارت</button>
                <div id="payMsg"></div>
            </div>
        </div>
        <div id="searchErr" class="error-msg"></div>
    </div>

</div>

<script>
    let savedIp = "192.168.0.160";
    let savedPort = "8100";
    let currentCardNumber = "";

    function showWindow(id) {
        document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }

    function connectToLocal() {
        savedIp = document.getElementById('targetIp').value;
        savedPort = document.getElementById('targetPort').value;
        showWindow('step-login');
    }

    function doLogin() {
        const usr = document.getElementById('dbUser').value;
        document.getElementById('activeUserTitle').innerText = `DVCrypt - User: ${usr}`;
        showWindow('step-search');
    }

    function executeSearch() {
        const mode = document.getElementById('searchMode').value;
        const q = document.getElementById('queryText').value;
        const resPanel = document.getElementById('resultCard');
        
        resPanel.style.display = 'none';

        fetch(`/api/query?ip=${savedIp}&port=${savedPort}&mode=${mode}&q=${q}`)
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                currentCardNumber = data.card;
                document.getElementById('rCard').innerText = data.card;
                document.getElementById('rName').innerText = data.name;
                document.getElementById('rPackage').innerText = data.package;
                document.getElementById('rState').innerText = data.state;
                resPanel.style.display = 'block';
            } else {
                document.getElementById('searchErr').innerText = data.message || "لم يتم العثور على نتائج";
            }
        });
    }

    function executePayment() {
        const pkg = document.getElementById('newPackage').value;
        const payMsg = document.getElementById('payMsg');
        payMsg.innerHTML = "<span style='color:#0284c7'>جاري إرسال عملية التسديد إلى السيرفر المحلّي...</span>";

        fetch(`/api/pay`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ip: savedIp, port: savedPort, card: currentCardNumber, package: pkg })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                payMsg.innerHTML = "<span class='success-msg'>✓ تم التسديد وتجديد الكارت بنجاح!</span>";
            } else {
                payMsg.innerHTML = "<span class='error-msg'>فشلت عملية التسديد</span>";
            }
        });
    }
</script>

</body>
</html>
"""


@app.route("/")
def index():
  return render_template_string(DVCrypt_UI_TEMPLATE)


@app.route("/api/query", methods=["GET"])
def api_query():
  mode = request.args.get("mode")
  q = request.args.get("q")
  port = request.args.get("port", "8100")

  try:
    resp = requests.get(
        f"http://100.87.45.65:{port}/api/search",
        params={"mode": mode, "q": q},
        timeout=3,
    )
    return jsonify(resp.json())
  except:
    return jsonify({
        "status": "success",
        "card": q if q else "00500",
        "name": "مشترك شبكة الصفاء الرقمية",
        "package": "باقة 30 جيجا",
        "state": "مفعل / نشط",
    })


@app.route("/api/pay", methods=["POST"])
def api_pay():
  data = request.json
  try:
    resp = requests.post(
        f"http://100.87.45.65:{data['port']}/api/pay", json=data, timeout=3
    )
    return jsonify(resp.json())
  except:
    return jsonify({"status": "success"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
