# DZExams Scraper

A Python command-line scraper for educational resources on dzexams.com.

This project provides a command-line interface in Arabic and English with Arabic text display support.

## What It Does
- Arabic and French interactive menus with keyboard navigation.
- Downloads organized by level, subject, and category.
- Optional year filtering and download limits.
- Retry logic with progress feedback for network failures.
- Windows-friendly file naming and safe `.part` downloads.

## Requirements
- Python 3.10 or newer.
- A terminal with UTF-8 support.
- On Windows, use Windows Terminal or PowerShell for the best display.
- Arabic shaping is enabled through `arabic-reshaper` and `python-bidi`; if those are missing, Arabic text may still print but will look less correct.

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
- استخدم تيرمينال تدعم UTF-8.
- يفضل استخدام Windows Terminal مع خط يدعم العربية مثل `Segoe UI` أو `Noto Sans Arabic`.
- تأكد من تثبيت `arabic-reshaper` و `python-bidi` لتحسين عرض النص العربي.

Downloaded files are stored under:

```text
downloads/<level>/<subject>/<category>/
```
