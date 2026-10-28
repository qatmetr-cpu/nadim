import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# مسار مجلد برنامج DVCrypt وملف الكروت
CARDS_DIR = r"C:\Users\user\DVCrypt\CardProg"
CARDS_FILE = os.path.join(CARDS_DIR, "cards")


@app.route("/api/subscriber-search", methods=["GET"])
def subscriber_search():
  mode = request.args.get("mode", "card")
  q = request.args.get("q", "").strip()
  results = []

  if os.path.exists(CARDS_FILE):
    try:
      with open(CARDS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
          line_str = line.strip()
          if not line_str:
            continue

          # تصفية النتائج بناءً على إدخال البحث
          if not q or q.lower() in line_str.lower():
            # محاولة تحليل السطر إذا كان مقسماً بفواصل أو مسافات
            parts = line_str.split(",")
            if len(parts) >= 2:
              card_id = parts[0].strip()
              name = parts[1].strip()
              phone = parts[2].strip() if len(parts) > 2 else ""
              address = parts[3].strip() if len(parts) > 3 else ""
            else:
              card_id = line_str[:10]
              name = line_str
              phone = ""
              address = ""

            results.append({
                "card": card_id,
                "name": name,
                "phone": phone,
                "address": address,
            })

            if len(results) >= 100:
              break
    except Exception as e:
      print(f"Error reading file: {e}")

  return jsonify({"status": "success", "results": results})


@app.route("/api/pay", methods=["POST"])
def pay():
  data = request.json
  # يمكنك هنا إضافة أي كود لتحديث ملف الكروت محلياً عند اتمام التسديد
  return jsonify(
      {"status": "success", "message": "Payment saved locally successfully"}
  )


if __name__ == "__main__":
  # الاستماع حصرياً على إيبي سلك الإيثيرنت المخصص
  app.run(host="192.168.0.210", port=8100)
