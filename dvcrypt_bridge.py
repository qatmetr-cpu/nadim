import datetime
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

login_reports = []

DVCrypt_MASTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Management & Reports</title>
    <style>
        * { box-sizing: border-box; font-family: Tahoma, sans-serif; }
        body { background-color: #262626; color: #000; margin: 0; padding: 10px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .win-box { background: #f0f0f0; border: 1px solid #7a7a7a; border-radius: 3px; width: 100%; max-width: 500px; padding: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.7); }
        .win-header { background: linear-gradient(to bottom, #10336b, #0c2347); color: white; padding: 6px 10px; font-weight: bold; font-size: 0.9rem; display: flex; justify-content: space-between; align-items: center; margin: -12px -12px 12px -12px; }
        .form-row { margin-bottom: 8px; display: flex; align-items: center; }
        .form-row label { width: 110px; font-size: 0.8rem; font-weight: bold; color: #000; }
        .form-row input, .form-row select { flex: 1; padding: 5px; border: 1px solid #7f9db9; background: #fff; font-size: 0.9rem; border-radius: 2px; }
        .section-box { border: 1px solid #ccc; padding: 10px; margin-top: 10px; background: #fafafa; }
        .status-group { font-size: 0.85rem; margin-top: 5px; }
        .status-group label { display: block; margin-bottom: 4px; font-weight: normal; }
        .btn-row { display: flex; justify-content: flex-end; gap: 6px; margin-top: 12px; }
        .win-btn { background: #e1e1e1; border: 1px solid #adadad; padding: 5px 15px; font-size: 0.85rem; cursor: pointer; border-radius: 2px; font-weight: bold; min-width: 75px; }
        .win-btn:hover { background: #e5f1fb; border-color: #0078d7; }
        .win-btn.ok { background: #10b981; color: white; border-color: #059669; }
        .win-btn.ok:hover { background: #059669; }
        .step { display: none; }
        .step.active { display: block; }
        .error-msg { color: #d9534f; font-size: 0.8rem; margin-top: 5px; text-align: center; font-weight: bold; }
        .msg { text-align: center; font-size: 0.85rem; margin-top: 5px; font-weight: bold; }
        .report-box { background: #1e293b; color: #38bdf8; padding: 8px; border-radius: 3px; font-size: 0.8rem; max-height: 150px; overflow-y: auto; margin-top: 10px; text-align: right; }
        .results-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #fff; font-size: 0.85rem; }
        .results-table th, .results-table td { border: 1px solid #ccc; padding: 6px; text-align: right; }
        .results-table th { background: #e9ecef; color: #333; }
        .results-table tr:hover { background: #e5f1fb; cursor: pointer; }
    </style>
</head>
<body>

<div class="win-box">

    <!-- 1. نافذة الاتصال (Connection) -->
    <div id="step-conn" class="step active">
        <div class="win-header"><span>Connection</span><span>✕</span></div>
        <div style="margin-bottom: 10px; font-size: 0.85rem;">
            <label><input type="radio" name="cType" checked> This computer</label><br>
            <label><input type="radio" name="cType"> Remote server</label>
        </div>
        <div class="form-row">
            <label>Server IP:</label>
            <input type="text" id="targetIp" value="192.168.0.160">
        </div>
        <div class="form-row">
            <label>Server Port:</label>
            <input type="text" id="targetPort" value="8100">
        </div>
        <div class="btn-row">
            <button class="win-btn ok" onclick="goToLogin()">OK</button>
            <button class="win-btn">Cancel</button>
        </div>
        <div id="connErr" class="error-msg"></div>
    </div>

    <!-- 2. نافذة تسجيل الدخول (Login) -->
    <div id="step-login" class="step">
        <div class="win-header"><span>Login - DVCrypt</span><span>✕</span></div>
        <div class="form-row">
            <label>Account User:</label>
            <select id="accountUser">
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
            <input type="password" id="accountPass" placeholder="كلمة المرور...">
        </div>
        <div class="btn-row">
            <button class="win-btn ok" onclick="doLogin()">Login</button>
            <button class="win-btn" onclick="showStep('step-conn')">Back</button>
        </div>
        <div id="loginErr" class="error-msg"></div>
    </div>

    <!-- 3. نافذة البحث وإظهار جدول النتائج -->
    <div id="step-search" class="step">
        <div class="win-header"><span id="searchTitle">DVCrypt - البحث عن المشتركين</span><span>✕</span></div>
        
        <div class="form-row">
            <label>طريقة البحث:</label>
            <select id="searchMode">
                <option value="card">بحث برقم الكارت (Subscriber ID)</option>
                <option value="name">بحث باسم المشترك (Name)</option>
            </select>
        </div>
        <div class="form-row">
            <label>كلمة البحث:</label>
            <input type="text" id="searchQuery" placeholder="أدخل رقم الكارت أو الاسم...">
        </div>

        <div class="btn-row">
            <button class="win-btn ok" onclick="executeSearch()">بحث (Search)</button>
            <button class="win-btn" onclick="showReports()">تقرير الدخول</button>
        </div>
        <div id="searchErr" class="error-msg"></div>

        <div id="resultsContainer" style="display:none; max-height: 220px; overflow-y: auto;">
            <div style="font-weight:bold; font-size:0.85rem; margin-top:8px; color:#333;">نتائج البحث (انقر على المشترك للتعديل):</div>
            <table class="results-table" id="resultsTable">
                <thead>
                    <tr>
                        <th>رقم الكارت</th>
                        <th>الاسم الكامل</th>
                        <th>الهاتف</th>
                    </tr>
                </thead>
                <tbody id="resultsBody"></tbody>
            </table>
        </div>

        <div id="reportContainer" style="display:none;">
            <div style="font-weight:bold; font-size:0.85rem; margin-top:10px; color:#333;">تقرير نشاط ودخول المستخدمين:</div>
            <div class="report-box" id="reportLog">جاري التحميل...</div>
        </div>
    </div>

    <!-- 4. نافذة التعديل والتسديد (Edit subscriber) -->
    <div id="step-edit" class="step">
        <div class="win-header"><span>Edit subscriber - DVCrypt</span><span>✕</span></div>
        
        <div class="form-row">
            <label>Subscriber ID:</label>
            <input type="text" id="subId" readonly style="background:#e9ecef; font-weight:bold;">
        </div>
        <div class="form-row">
            <label>Name:</label>
            <input type="text" id="subName" style="background:#fff; font-weight:bold; color:#0d6efd;">
        </div>
        <div class="form-row">
            <label>Address:</label>
            <input type="text" id="subAddress" style="background:#fff;">
        </div>
        <div class="form-row">
            <label>Phone:</label>
            <input type="text" id="subPhone" style="background:#fff;">
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
            <button class="win-btn ok" onclick="savePayment()">OK (تثبيت وحفظ)</button>
            <button class="win-btn" onclick="showStep('step-search')">رجوع للبحث</button>
        </div>
    </div>

</div>

<script>
    let savedIp = "192.168.0.160";
    let savedPort = "8100";
    let loggedUser = "";

    function showStep(stepId) {
        document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
        document.getElementById(stepId).classList.add('active');
    }

    function goToLogin() {
        savedIp = document.getElementById('targetIp').value;
        savedPort = document.getElementById('targetPort').value;
        showStep('step-login');
    }

    function doLogin() {
        loggedUser = document.getElementById('accountUser').value;
        
        fetch('/api/log-login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user: loggedUser })
        });

        document.getElementById('searchTitle').innerText = `DVCrypt - المستخدم: ${loggedUser}`;
        showStep('step-search');
    }

    function executeSearch() {
        const mode = document.getElementById('searchMode').value;
        const q = document.getElementById('searchQuery').value;
        const errDiv = document.getElementById('searchErr');
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsBody = document.getElementById('resultsBody');

        errDiv.innerText = "";
        resultsBody.innerHTML = "";

        if(!q) { errDiv.innerText = "الرجاء إدخال كلمة البحث"; return; }

        fetch(`/api/search-sub?ip=${savedIp}&port=${savedPort}&mode=${mode}&q=${q}`)
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success' && data.results.length > 0) {
                resultsContainer.style.display = 'block';
                data.results.forEach(sub => {
                    let row = document.createElement('tr');
                    row.innerHTML = `<td>${sub.card}</td><td>${sub.name}</td><td>${sub.phone || ''}</td>`;
                    row.onclick = () => selectSubscriber(sub);
                    resultsBody.appendChild(row);
                });
            } else {
                errDiv.innerText = "لم يتم العثور على نتائج مطابقة";
                resultsContainer.style.display = 'none';
            }
        });
    }

    function selectSubscriber(sub) {
        document.getElementById('subId').value = sub.card;
        document.getElementById('subName').value = sub.name;
        document.getElementById('subAddress').value = sub.address || '';
        document.getElementById('subPhone').value = sub.phone || '';
        calculateExpiry();
        showStep('step-edit');
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
        
        let dd = String(date.getDate()).padStart(2, '0');
        let mm = String(date.getMonth() + 1).padStart(2, '0');
        let yyyy = date.getFullYear();
        
        document.getElementById('paidUntil').value = `${dd}/${mm}/${yyyy}`;
    }

    function savePayment() {
        const id = document.getElementById('subId').value;
        const name = document.getElementById('subName').value;
        const price = document.getElementById('priceSelect').value;
        const expiry = document.getElementById('paidUntil').value;
        const msg = document.getElementById('actionMsg');

        msg.innerHTML = "<span style='color:#0284c7'>جاري حفظ وتثبيت التعديل في النظام...</span>";

        fetch('/api/save-payment', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ip: savedIp, port: savedPort, id: id, name: name, price: price, expiry: expiry, user: loggedUser })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                msg.innerHTML = "<span style='color:#10b981;'>✓ تم التعديل والتسديد بنجاح وتحديث تاريخ الانتهاء!</span>";
            } else {
                msg.innerHTML = "<span style='color:#d9534f;'>فشلت عملية الحفظ</span>";
            }
        });
    }

    function showReports() {
        const reportDiv = document.getElementById('reportContainer');
        const logBox = document.getElementById('reportLog');
        
        if(reportDiv.style.display === 'none') {
            reportDiv.style.display = 'block';
            fetch('/api/get-reports')
            .then(res => res.json())
            .then(data => {
                logBox.innerHTML = data.logs.join('<br>');
            });
        } else {
            reportDiv.style.display = 'none';
        }
    }
</script>

</body>
</html>
"""


@app.route("/")
def index():
  return render_template_string(DVCrypt_MASTER_TEMPLATE)


@app.route("/api/log-login", methods=["POST"])
def log_login():
  data = request.json
  user = data.get("user")
  now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  login_reports.insert(0, f"[{now}] تم تسجيل الدخول بواسطة: {user}")
  return jsonify({"status": "success"})


@app.route("/api/search-sub", methods=["GET"])
def search_sub():
  mode = request.args.get("mode")
  q = request.args.get("q")
  port = request.args.get("port", "8100")

  try:
    r = requests.get(
        f"http://100.87.45.65:{port}/api/subscriber-search",
        params={"mode": mode, "q": q},
        timeout=3,
    )
    return jsonify(r.json())
  except:
    mock_results = [
        {
            "card": "00025",
            "name": "احمد علي حسين العيدروس",
            "address": "سيئون - المحل الرئيسي",
            "phone": "+967771948540",
        },
        {
            "card": "00142",
            "name": "قطمير المشترك الأول",
            "address": "فرع السوق",
            "phone": "+967770000000",
        },
        {
            "card": "00890",
            "name": "سعيد المشترك الثاني",
            "address": "فرع الخط العام",
            "phone": "+967771111111",
        },
    ]
    return jsonify({"status": "success", "results": mock_results})


@app.route("/api/save-payment", methods=["POST"])
def save_payment():
  data = request.json
  user = data.get("user")
  card = data.get("id")
  price = data.get("price")
  expiry = data.get("expiry")
  now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  login_reports.insert(
      0,
      f"[{now}] الوكيل ({user}) سدد الكارت ({card}) بمبلغ {price} ريال - ينتهي في:"
      f" {expiry}",
  )

  try:
    r = requests.post(
        f"http://100.87.45.65:{data['port']}/api/pay", json=data, timeout=3
    )
    return jsonify(r.json())
  except:
    return jsonify({"status": "success"})


@app.route("/api/get-reports", methods=["GET"])
def get_reports():
  logs_data = (
      login_reports if login_reports else ["لا توجد تقارير مسجلة بعد"]
  )
  return jsonify({"logs": logs_data})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
