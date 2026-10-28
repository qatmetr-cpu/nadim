import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# عنوان جهاز الكمبيوتر الأساسي في محلك عبر شبكة الـ VPN الخاصة (Tailscale)
LOCAL_PC_DVCrypt_URL = "http://100.87.45.65:8100"


@app.route("/api/search", methods=["GET"])
def cloud_search():
  card_no = request.args.get("card")

  if not card_no:
    return jsonify({"status": "error", "message": "الرجاء إدخال رقم الكارت"}), 400

  try:
    # السحابة تستعلم مباشرة من جهاز الكمبيوتر في محلك عبر نفق الـ VPN الآمن
    response = requests.get(
        f"{LOCAL_PC_DVCrypt_URL}/api/search", params={"card": card_no}, timeout=3
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
        "message": "تعذر الوصول إلى الكمبيوتر الأساسي (تأكد من تشغيل الكمبيوتر والـ VPN)",
        "details": str(e),
    }), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
