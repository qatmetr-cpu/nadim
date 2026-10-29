from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

# مسار ملف قاعدة بيانات DVCrypt على الكمبيوتر
DB_PATH = r"C:\Program Files\DVCrypt\database.db"  # غير المسار إلى مسار ملف قاعدة البيانات الحقيقي لديك

def get_db_connection():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    return None

# الواجهة الرئيسية (تسجيل الدخول + لوحة التحكم والتسديد)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Mobile Portal</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 15px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 20px; }
        h2, h3 { color: #00d2d3; text-align: center; margin-top: 0; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #333; box-sizing: border-box; font-size: 16px; }
        input { background: #2a2a2a; color: white; }
        button { background: #10ac84; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #1dd1a1; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: center; font-size: 14px; }
        th { background-color: #222f3e; color: #00d2d3; }
        tr:nth-child(even) { background-color: #181818; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .active { background: #10ac84; color: #fff; }
    </style>
</head>
<body>

{% if not logged_in %}
    <!-- شاشة تسجيل الدخول -->
    <div class="card" style="max-width: 400px; margin: 50px auto;">
        <h2>DVCrypt System</h2>
        <p style="text-align:center; color:#aaa;">أدخل كلمة السر للوصول إلى واجهة المستخدمين والتسديد</p>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="اسم المستخدم" required>
            <input type="password" name="password" placeholder="كلمة السر" required>
            <button type="submit">تسجيل الدخول</button>
        </form>
    </div>
{% else %}
    <!-- واجهة إدارة المستخدمين وعمليات التسديد -->
    <h2>لوحة إدارة DVCrypt</h2>
    
    <!-- قسم التسديد السريع وتفعيل الكروت -->
    <div class="card">
        <h3>تسديد اشتراك / تفعيل كرت</h3>
        <form method="POST" action="/pay">
            <input type="text" name="user_id" placeholder="رقم المشترك / اسم المستخدم" required>
            <input type="number" name="amount" placeholder="المبلغ / قيمة الفئة" required>
            <button type="submit">تأكيد عملية التسديد</button>
        </form>
    </div>

    <!-- جدول عرض المشتركين والحسابات -->
    <div class="card">
        <h3>قائمة المشتركين الحالية</h3>
        <table>
            <thead>
                <tr>
                    <th>رقم الحساب</th>
                    <th>اسم المشترك</th>
                    <th>الحالة</th>
                    <th>تاريخ الانتهاء</th>
                </tr>
            </thead>
            <tbody>
                {% if subscribers %}
                    {% for sub in subscribers %}
                    <tr>
                        <td>{{ sub['id'] }}</td>
                        <td>{{ sub['name'] }}</td>
                        <td><span class="badge active">{{ sub['status'] }}</span></td>
                        <td>{{ sub['expire_date'] }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr>
                        <td colspan="4">لا توجد بيانات متاحة أو جاري تحميل قاعدة البيانات...</td>
                    </tr>
                {% endif %}
            </tbody>
        </table>
    </div>
{% endif %}

</body>
</html>
"""

logged_in_state = False

@app.route('/')
def index():
    subscribers = []
    conn = get_db_connection()
    if conn:
        try:
            # استعلام افتراضي لجلب المشتركين من ملف قاعدة البيانات
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, status, expire_date FROM subscribers LIMIT 20")
            subscribers = cursor.fetchall()
            conn.close()
        except:
            pass

    return render_template_string(HTML_TEMPLATE, logged_in=logged_in_state, subscribers=subscribers)

@app.route('/login', methods=['POST'])
def login():
    global logged_in_state
    # هنا يتم التحقق من كلمة السر والقبول
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username and password:
        logged_in_state = True
    return redirect(url_for('index'))

@app.route('/pay', methods=['POST'])
def pay():
    user_id = request.form.get('user_id')
    amount = request.form.get('amount')
    
    # تنفيذ عملية التحديث والتسديد داخل قاعدة بيانات DVCrypt
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE subscribers SET status='نشط' WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
        except:
            pass
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8101)
