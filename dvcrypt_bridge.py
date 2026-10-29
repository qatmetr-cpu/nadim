from flask import Flask, render_template_string, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

# مسار قاعدة بيانات برنامج DVCrypt على جهاز الكمبيوتر الرئيسي
# (تأكد من مطابقة المسار تماماً لمكان قاعدة بيانات البرنامج لديك)
DB_PATH = r"C:\Program Files\DVCrypt\database.db"

def get_db_connection():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    return None

# قالب الواجهة المطابق لنظام DVCrypt مع أداة البحث وإدارة الكروت
TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Remote Client</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #2f3640; color: #f5f6fa; margin: 0; padding: 10px; }
        .header { background: #192a56; padding: 10px; text-align: center; border-radius: 6px; margin-bottom: 10px; }
        .card { background: #353b48; padding: 15px; border-radius: 6px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        input, select, button { width: 100%; padding: 10px; margin: 6px 0; border-radius: 4px; border: 1px solid #718093; box-sizing: border-box; background: #2f3640; color: #fff; font-size: 14px; }
        button { background: #4cd137; color: #fff; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #44bd32; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { border: 1px solid #718093; padding: 8px; text-align: center; }
        th { background: #273c75; color: #fbc531; }
        tr:nth-child(even) { background: #2f3640; }
        .active { color: #4cd137; font-weight: bold; }
        .ended { color: #e84118; font-weight: bold; }
        .search-box { display: flex; gap: 5px; }
        .search-box input { flex: 3; }
        .search-box button { flex: 1; }
    </style>
</head>
<body>

<div class="header">
    <h3>DVCrypt Client - Remote Management</h3>
    <span style="font-size: 12px; color: #00d2d3;">السرعة والاتصال متصل بـ 192.168.0.160:8100</span>
</div>

<!-- أداة البحث برقم الكرت أو اسم المشترك -->
<div class="card">
    <form method="GET" action="/">
        <label><b>بحث عن مشترك (رقم الكرت أو الاسم):</b></label>
        <div class="search-box">
            <input type="text" name="q" value="{{ query }}" placeholder="أدخل رقم الحساب ID أو اسم المشترك...">
            <button type="submit">بحث</button>
        </div>
    </form>
</div>

<!-- جدول عرض المشتركين وتفاصيل الاشتراكات -->
<div class="card">
    <h3>قائمة المشتركين (Subscribers)</h3>
    <div style="overflow-x: auto;">
        <table>
            <thead>
                <tr>
                    <th>Subscriber ID</th>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Status</th>
                    <th>Paid Untill</th>
                </tr>
            </thead>
            <tbody>
                {% if subscribers %}
                    {% for sub in subscribers %}
                    <tr>
                        <td>{{ sub['id'] }}</td>
                        <td>{{ sub['name'] }}</td>
                        <td>{{ sub['phone'] }}</td>
                        <td>
                            {% if sub['status'] == 'Active' or sub['status'] == 'نشط' %}
                                <span class="active">Active</span>
                            {% else %}
                                <span class="ended">Subscription ended</span>
                            {% endif %}
                        </td>
                        <td>{{ sub['expire_date'] }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr>
                        <td colspan="5">لا توجد نتائج مطابقة أو جاري قراءة قاعدة البيانات...</td>
                    </tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>

</body>
</html>
"""

@app.route('/')
def index():
    query = request.args.get('q', '')
    subscribers = []
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if query:
                # تنفيذ البحث برقم الحساب أو الاسم داخل قاعدة البيانات
                sql = "SELECT id, name, phone, status, expire_date FROM subscribers WHERE id LIKE ? OR name LIKE ? LIMIT 50"
                cursor.execute(sql, (f'%{query}%', f'%{query}%'))
            else:
                cursor.execute("SELECT id, name, phone, status, expire_date FROM subscribers LIMIT 50")
            subscribers = cursor.fetchall()
            conn.close()
        except Exception as e:
            print("DB Error:", e)
            
    return render_template_string(TEMPLATE, subscribers=subscribers, query=query)

if __name__ == '__main__':
    # تشغيل السيرفر على منفذ الاتصال المخصص
    app.run(host='0.0.0.0', port=8100)
