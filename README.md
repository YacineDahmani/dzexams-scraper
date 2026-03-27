# DZExams Scraper

A Python command-line scraper for educational resources on dzexams.com.

هذا المشروع يقدم واجهة سطر أوامر باللغة العربية والإنجليزية مع دعم عرض النص العربي.

This project provides a command-line interface in Arabic and English with Arabic text display support.

## What It Does
- Arabic and English interactive menus with keyboard navigation.
- Downloads organized by level, subject, and category.
- Optional year filtering and download limits.
- Retry logic with progress feedback for network failures.
- Windows-friendly file naming and safe `.part` downloads.

## ماذا يفعل التطبيق
- قوائم تفاعلية بالعربية والإنجليزية مع التنقل عبر لوحة المفاتيح.
- تنزيل الملفات بشكل منظم حسب المرحلة والمادة والفئة.
- إمكانية تصفية السنة وتحديد حد أقصى للتنزيل.
- منطق إعادة المحاولة مع عرض التقدم عند حدوث مشاكل في الشبكة.
- أسماء ملفات مناسبة لويندوز مع حفظ آمن بامتداد `.part`.

## Requirements
- Python 3.10 or newer.
- A terminal with UTF-8 support.
- On Windows, use Windows Terminal or PowerShell for the best display.
- Arabic shaping is enabled through `arabic-reshaper` and `python-bidi`; if those are missing, Arabic text may still print but will look less correct.

## المتطلبات
- Python 3.10 أو أحدث.
- طرفية تدعم UTF-8.
- على Windows، يفضل استخدام Windows Terminal أو PowerShell للحصول على أفضل عرض.
- يتم تحسين تشكيل النص العربي عبر `arabic-reshaper` و `python-bidi`، وإذا لم تكونا مثبتتين فقد يظهر النص العربي بشكل أقل دقة.

## الإعداد

1. انسخ المستودع:
   ```bash
   git clone https://github.com/YacineDahmani/dzexams-scraper.git
   cd dzexams-scraper
   ```

2. أنشئ بيئة افتراضية وقم بتفعيلها:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. ثبّت المتطلبات:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper:

```bash
python main.py
```

You will be asked to choose:
- the study stage,
- the school year,
- the subject,
- the category,
- an optional year filter,
- and an optional download limit.

إذا ظهرت بعض الخيارات أو المحتويات بالعربية، فسيتم عرضها عبر أدوات العرض الخاصة بالتطبيق لتبقى مقروءة في طرفيات Windows التي تدعم العربية.

At startup, the app shows Arabic and English menus. For the best display on Windows:
- Use a UTF-8 capable terminal.
- Prefer Windows Terminal with an Arabic-capable font such as `Segoe UI` or `Noto Sans Arabic`.
- Make sure `arabic-reshaper` and `python-bidi` are installed for better Arabic rendering.

## الاستخدام

شغّل أداة التنزيل:

```bash
python main.py
```

سيُطلب منك اختيار:
- المرحلة الدراسية
- السنة الدراسية
- المادة
- الفئة
- فلتر اختياري للسنة
- وحد أقصى اختياري لعدد الملفات التي سيتم تنزيلها

عند بدء التشغيل، يعرض التطبيق القوائم بالعربية والإنجليزية. ولأفضل عرض على Windows:
- استخدم طرفية تدعم UTF-8.
- يفضل استخدام Windows Terminal مع خط يدعم العربية مثل `Segoe UI` أو `Noto Sans Arabic`.
- تأكد من تثبيت `arabic-reshaper` و `python-bidi` لتحسين عرض النص العربي.

Downloaded files are stored under:

```text
downloads/<level>/<subject>/<category>/
```

## Project Notes
- `.gitignore` excludes virtual environments, generated downloads, and Python cache files.
- The downloader saves to a temporary `.part` file first, then renames it atomically after success.
- Arabic strings are routed through the display helpers to keep the console output readable.

## ملاحظات المشروع
- يستثني `.gitignore` بيئات Python الافتراضية وملفات التنزيل الناتجة وملفات التخزين المؤقت.
- يحفظ برنامج التنزيل الملف مؤقتًا بامتداد `.part` ثم يعيد تسميته بشكل آمن بعد النجاح.
- تمرر النصوص العربية عبر أدوات العرض للحفاظ على وضوح الإخراج في الطرفية.

## Disclaimer

This tool is intended for educational use only. Respect dzexams.com terms of service and robots rules when scraping.

## إخلاء المسؤولية

هذا التطبيق مخصص للاستخدام التعليمي فقط. يرجى احترام شروط استخدام dzexams.com وقواعد robots عند تنفيذ عمليات scraping.
