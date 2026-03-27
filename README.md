# DZExams Scraper

A Python command-line scraper for educational resources on dzexams.com.

## What It Does
- Arabic interactive menu flow with keyboard navigation.
- Downloads organized by level, subject, and category.
- Optional year filtering and download limits.
- Retry logic with progress feedback for network failures.
- Windows-friendly file naming and safe `.part` downloads.

## Requirements
- Python 3.10 or newer.
- A terminal with UTF-8 support.
- On Windows, use Windows Terminal or PowerShell for the best Arabic rendering.

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

## Arabic CLI Setup

The app prepares the console for Arabic output at startup. For the cleanest display on Windows:
- Keep the terminal encoding set to UTF-8.
- Use a font that supports Arabic glyphs, such as Cairo, Segoe UI, or Noto Sans Arabic.
- If Arabic text looks reversed or disconnected, restart the terminal after activation.

The CLI uses shaping and bidi helpers when available, and falls back safely if those packages are missing.

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
- Arabic strings are routed through the display helpers to keep the console output readable.

## Disclaimer

This tool is intended for educational use only. Respect dzexams.com terms of service and robots rules when scraping.
