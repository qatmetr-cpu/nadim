import os
import socket
from flask import Flask, jsonify, request

app = Flask(__name__)

# المسار المباشر لملف السجلات داخل مجلد البرنامج
LOG_FILE_PATH = r"C:\Users\user\DVCrypt\log_2.txt"  # أكتب المسار الصحيح تماماً هنا


@app.route("/api/search", methods=["GET"])
def search_card():
  card_no = request.args.get("card")

  if not card_no:
    return jsonify({"status": "error", "message": "الرجاء إدخال رقم الكارت"}), 400

  formatted_card = card_no.zfill(6)
  subscriber_name = f"مشترك ({card_no})"
  state_info = "Not used"
  package_info = "باقة معتمدة"
  details_info = "لم يتم العثور على بيانات مطابقة"

  try:
    if os.path.exists(LOG_FILE_PATH):
      with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for line in reversed(lines):
          if card_no in line or formatted_card in line:
            if "Active" in line or "Activated" in line:
              state_info = "Active"
              details_info = "الاشتراك نشط وفعال"
            elif "ended" in line or "Subscription ended" in line:
              state_info = "Subscription ended"
              details_info = "انتهت صلاحية الاشتراك"
            elif "subscription date changed" in line:
              state_info = "Active"
              details_info = "تم تحديث تاريخ الاشتراك بنجاح"
            break
    else:
      details_info = "ملف السجل غير موجود في المسار المحدد"
  except Exception as e:
    details_info = f"خطأ في قراءة البيانات: {str(e)}"

  return jsonify({
      "status": "success",
      "card": card_no,
      "subscriber_name": subscriber_name,
      "state": state_info,
      "package": package_info,
      "details": details_info,
  })


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
