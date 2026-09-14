# مرافق Shizuku Helper - مشروع Android كامل

تطبيق بنفس واجهة الصورة: حالة Shizuku، استخراج الملفات، تثبيت واتساب قديم، استعادة نسخة احتياطية، ولوحة سجلات.

## خطوات التشغيل والحصول على APK

1. ثبّت **Android Studio** (أحدث إصدار).
2. افتح هذا المجلد كمشروع (Open → حدد مجلد ShizukuHelperApp).
3. انتظر حتى ينتهي Gradle Sync (يتطلب إنترنت أول مرة).
4. استبدل ملفات الوهمية في `app/src/main/assets/` بالملفات الحقيقية:
   - `alriqi.ab`  ← النسخة الاحتياطية
   - `w.apk`      ← ملف واتساب القديم
   - `shizuku.apk` ← ملف تطبيق Shizuku
5. للحصول على APK:
   - Build → Build Bundle(s)/APK(s) → Build APK(s)
   - أو Build → Generate Signed Bundle/APK للنسخة الموقعة

## الحصول على APK بدون تثبيت شيء (GitHub Actions) ⭐

أسهل طريقة — البناء سحابي ومجاني تماماً:

1. أنشئ حساباً مجانياً على **github.com**
2. اضغط **New Repository** → اسمها مثلاً `ShizukuHelper` → اجعلها Public → Create
3. اضغط **uploading an existing file** واسحب كل ملفات المشروع (أو ارفع ملف ZIP بعد فكّه)
4. انتظر دقيقتين — سيبدأ البناء تلقائياً (شاهده من تبويب **Actions**)
5. عند ظهور علامة ✅ خضراء، افتح **Actions** → اضغط آخر تشغيل → **Artifacts** → حمّل **ShizukuHelper-APK**
6. انقل الملف `app-debug.apk` إلى هاتفك وثبّته (اسمح بتثبيت التطبيقات من مصادر خارجية)

> ملاحظة: يمكنك إعادة البناء في أي وقت بضغطة زر من تبويب Actions → **Run workflow**

## كيف يعمل

- **طلب الإذن**: يستخدم مكتبة Shizuku الرسمية (`dev.rikka.shizuku:api`) لطلب إذن المستخدم.
- **استخراج الملفات**: ينسخ الملفات من assets إلى مجلد التنزيلات ويسجّل الحجم والمسار في لوحة السجلات مع وسوم [SUCCESS].
- **تثبيت واتساب قديم**: يثبّت `w.apk` عبر FileProvider.
- **استعادة النسخة**: يشغّل أوامر shell عبر Shizuku بعد منح الإذن.

## ملاحظات

- `minSdk = 24` و `targetSdk = 34` — يعمل من أندرويد 7 فما فوق.
- يجب تثبيت تطبيق Shizuku على الجهاز وبدء خدمته (عبر ADB أو Wireless debugging) قبل منح الإذن.
- الألوان والتصميم مطابقة للواجهة في الصورة (خلفية داكنة، أزرار ملوّنة، لوحة سجلات خضراء).

## الأوامر الحقيقية عبر Shizuku (Shell / ADB)

التطبيق يستخدم `Shizuku.newProcess()` لتنفيذ أوامر shell **بصلاحيات ADB** (uid=shell) بدون root:

| العملية | الأمر المُنفَّذ |
|---|---|
| طلب الإذن | `Shizuku.requestPermission()` (واجهة النظام) |
| التحقق من الملفات | `ls -lh /sdcard/Download/` |
| التثبيت الصامت | `pm install -r /sdcard/Download/w.apk` (بدون شاشة التثبيت!) |
| الاستعادة | `cp` + `chmod 644` + `pm list packages` |

### بنية الكود
- `ShizukuShell.kt`: كائن (Object) منفصل يوفّر:
  - `isServiceRunning()` — فحص ping للـ Binder
  - `isPermissionGranted()` — فحص الإذن
  - `exec(cmd)` — تنفيذ أمر مع timeout وقراءة stdout/stderr
  - `execBatch(commands)` — تنفيذ سلسلة أوامر مع إيقاف عند الخطأ
- الملفات تُنفَّذ في `Thread` منفصل حتى لا يتجمد الواجهة، والنتائج تظهر في لوحة السجلات بوسوم `[CMD]` `[SUCCESS]` `[ERR]`.

### تشغيل Shizuku على الجهاز (مرة واحدة)
```bash
adb shell sh /sdcard/Android/data/moe.shizuku.privileged.api/start.sh
```
أو عبر Wireless Debugging من داخل تطبيق Shizuku نفسه (أندرويد 11+).
