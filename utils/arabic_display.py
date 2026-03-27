import os
import sys

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except Exception:  # optional dependency fallback
    arabic_reshaper = None
    get_display = None


def _shape(text):
    if text is None:
        return text
    if arabic_reshaper is None or get_display is None:
        return str(text)
    return get_display(arabic_reshaper.reshape(str(text)))


def display_text(text):
    return _shape(text)


def display_prompt(text):
    return _shape(text)


def configure_console_encoding():
    try:
        os.environ.setdefault("PYTHONUTF8", "1")
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        if os.name == "nt":
            # Best effort: switch active code page to UTF-8 for Windows terminals.
            os.system("chcp 65001 >NUL")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass