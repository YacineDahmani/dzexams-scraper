# DZExams Scraper

A Python command-line scraper for educational resources on dzexams.com.

Ce projet propose une interface CLI en francais.

## What It Does
- French interactive menu flow with keyboard navigation.
- Downloads organized by level, subject, and category.
- Optional year filtering and download limits.
- Retry logic with progress feedback for network failures.
- Windows-friendly file naming and safe `.part` downloads.

## Requirements
- Python 3.10 or newer.
- A terminal with UTF-8 support.
- On Windows, use Windows Terminal or PowerShell for the best display.
- Arabic shaping is enabled through `arabic-reshaper` and `python-bidi`; if those are missing, Arabic text may still print but will look less correct.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YacineDahmani/dzexams-scraper.git
   cd dzexams-scraper
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Instructions en francais

Au demarrage, l'application affiche les menus en francais. Pour un rendu correct sous Windows:
- Utilisez un terminal compatible UTF-8.
- Prefer Windows Terminal with an Arabic-capable font such as `Segoe UI` or `Noto Sans Arabic`.

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

Downloaded files are stored under:

```text
downloads/<level>/<subject>/<category>/
```

## Project Notes
- `.gitignore` excludes virtual environments, generated downloads, and Python cache files.
- The downloader saves to a temporary `.part` file first, then renames it atomically after success.
- French strings are routed through the display helpers to keep the console output readable.

## Disclaimer

This tool is intended for educational use only. Respect dzexams.com terms of service and robots rules when scraping.
