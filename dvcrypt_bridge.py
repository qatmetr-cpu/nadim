import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# عنوان جهاز الكمبيوتر الأساسي في المحل عبر شبكة Tailscale VPN الثابتة
LOCAL_PC_DVCrypt_URL = "http://100.87.45.65:8100"

# قالب واجهة الويب المطابق لنظام DVCrypt
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة شبكة ALSAFA TV</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: #1e293b; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { text-align: center; color: #38bdf8; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #cbd5e1; }
        input { width: 100%; padding: 10px; box-sizing: border-box; background: #0f172a; border: 1px solid #475569; color: #fff; border-radius: 5px; font-size: 16px; }
        button { width: 100%; padding: 12px; background: #0284c7; border: none; color: white; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; transition: 0.3s; }
        button:hover { background: #0369a1; }
        .result-box { margin-top: 20px; background: #0f172a; padding: 15px; border-radius: 5px; border-right: 4px solid #38bdf8; display: none; }
        .result-item { margin-bottom: 8px; }
        .error { color: #f87171; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🌐 نظام إدارة شبكة ALSAFA TV</h2>
        <div class="form-group">
            <label>رقم الكارت:</label>
            <input type="text" id="cardInput" placeholder="أدخل رقم الكارت (مثال: 00500)">
        </div>
        <button onclick="searchCard()">بحث عن الكارت</button>
        <div id="errorMsg" class="error"></div>

        <div id="resultBox" class="result-box">
            <div class="result-item"><strong>رقم الكارت:</strong> <span id="resCard"></span></div>
            <div class="result-item"><strong>اسم المشترك:</strong> <span id="resName"></span></div>
            <div class="result-item"><strong>الحالة:</strong> <span id="resState"></span></div>
            <div class="result-item"><strong>الباقة الحالية:</strong> <span id="resPackage"></span></div>
            <div class="result-item"><strong>التفاصيل:</strong> <span id="resDetails"></span></div>
        </div>
    </div>

    <script>
        function searchCard() {
            const cardNo = document.getElementById('cardInput').value;
            const errorMsg = document.getElementById('errorMsg');
            const resultBox = document.getElementById('resultBox');

            errorMsg.innerText = "";
            resultBox.style.display = "none";

            if (!cardNo) {
                errorMsg.innerText = "الرجاء إدخال رقم الكارت أولاً";
                return;
            }

            fetch(`/api/search?card=${cardNo}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('resCard').innerText = data.card;
                        document.getElementById('resName').innerText = data.subscriber_name;
                        document.getElementById('resState').innerText = data.state;
                        document.getElementById('resPackage').innerText = data.package;
                        document.getElementById('resDetails').innerText = data.details;
                        resultBox.style.display = 'block';
                    } else {
                        errorMsg.innerText = data.message || "حدث خطأ أثناء البحث";
                    }
                })
                .catch(err => {
                    errorMsg.innerText = "تعذر الاتصال بالسيرفر المحلي عبر الشبكة الآمنة";
                });
        }
    </script>
</body>
</html>
"""


@app.route("/")
def home():
  return render_template_string(HTML_TEMPLATE)


@app.route("/api/search", methods=["GET"])
def cloud_search():
  card_no = request.args.get("card")

  if not card_no:
    return jsonify({"status": "error", "message": "الرجاء إدخال رقم الكارت"}), 400

  try:
    # تمرير الطلب من السحابة إلى جهازك المحلي في المحل عبر نفق Tailscale الآمن
    response = requests.get(
        f"{LOCAL_PC_DVCrypt_URL}/api/search", params={"card": card_no}, timeout=4
    )

    if response.status_code == 200:
      return jsonify(response.json())
    else:
      return jsonify({
          "status": "error",
          "message": "استجابة غير صالحة من برنامج DVCrypt على الكمبيوتر المحلي",
      }), 500

  except Exception as e:
    return jsonify({
        "status": "error",
        "message": (
            "تعذر الوصول إلى الكمبيوتر الرئيسي في المحل (تأكد من تشغيل الكمبيوتر"
            " والـ VPN)"
        ),
        "details": str(e),
    }), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
