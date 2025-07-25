# أداة استخراج جافاسكريبت وCSS وSass من HTML (واجهة رسومية)

هذه الأداة تتيح لك استخراج ملفات الجافاسكريبت وCSS وSass من ملفات HTML بسهولة عبر واجهة رسومية. يمكنك تنظيم الملفات الناتجة في هيكل مشروع قياسي، وتحويل Sass إلى CSS إذا رغبت بذلك.

---

## الميزات
- استخراج JS وCSS وSass من ملفات HTML
- معالجة عدة ملفات دفعة واحدة
- تحويل Sass إلى CSS (يتطلب libsass)
- تصغير الملفات الناتجة
- الحفاظ على التعليقات أو إزالتها
- إنشاء نسخة احتياطية من HTML الأصلي
- تعليمات عربية بالكامل

---

## التثبيت

1. يتطلب بايثون 3.7 أو أحدث
2. ثبّت المتطلبات:

```bash
pip install -r requirements.txt
```

لدعم Sass:
```bash
pip install libsass
```

---

## 🚀 البدء السريع

### على لينكس
1. افتح الطرفية (Terminal).
2. تأكد من وجود بايثون 3:
   ```bash
   python3 --version
   ```
   إذا لم يكن مثبتًا:
   ```bash
   sudo apt update && sudo apt install python3 python3-pip
   ```
3. ثبّت المتطلبات:
   ```bash
   pip3 install -r requirements.txt
   ```
4. شغّل البرنامج:
   ```bash
   python3 gui_html_extractor.py
   ```

### على ويندوز
1. افتح موجه الأوامر (Command Prompt).
2. تأكد من وجود بايثون:
   ```cmd
   python --version
   ```
   إذا لم يكن مثبتًا، نزّل بايثون من [python.org](https://www.python.org/downloads/) وثبته.
3. ثبّت المتطلبات:
   ```cmd
   pip install -r requirements.txt
   ```
4. شغّل البرنامج:
   ```cmd
   python gui_html_extractor.py
   ```

---

## المتطلبات
- Python 3.7+
- tkinter (عادةً مرفق مع بايثون)
- libsass (اختياري)

---

## لقطات الشاشة

**الواجهة الرئيسية**

![الواجهة الرئيسية](Screenshot_20250724_020841.png)

**مثال على سجل الاستخراج**

![سجل الاستخراج](Screenshot_20250724_020711.png)

---

## المؤلف
- محمد

---

## الرخصة
MIT 

---

## لقطات الشاشة

**الواجهة الرئيسية**

![الواجهة الرئيسية](Screenshot_20250724_020841.png)

**مثال على سجل الاستخراج**

![سجل الاستخراج](Screenshot_20250724_020711.png)

--- 