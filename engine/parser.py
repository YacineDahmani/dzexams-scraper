import time
import random
import re
import base64
import requests
from bs4 import BeautifulSoup
from utils.translator import BASE_URL
from utils.logger import log

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

YEAR_PATTERN = re.compile(r"(?:19|20)\d{2}")


def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "ar,fr;q=0.9,en;q=0.8",
    })
    return session


def _to_absolute_url(href):
    if not href:
        return None
    return href if href.startswith("http") else BASE_URL + href


def decode_data_id(encoded_id):
    """Decode DZExams card data-id into the real slug used in /ar/sujets/<slug>."""
    if not encoded_id:
        return None

    try:
        raw = base64.b64decode(encoded_id).decode("latin1")
        return "".join(chr(ord(ch) - 8) for ch in raw)
    except Exception:
        return None


def extract_years(text):
    if not text:
        return []
    years = YEAR_PATTERN.findall(text)
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(years))


def normalize_year_filter(year_filter):
    if not year_filter:
        return None

    value = str(year_filter).strip()
    if not value:
        return None

    # Support range filters such as 2022-2024.
    range_match = re.fullmatch(r"\s*((?:19|20)\d{2})\s*[-/]\s*((?:19|20)\d{2})\s*", value)
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        if start > end:
            start, end = end, start
        if end - start > 30:
            raise ValueError("نطاق السنوات كبير جدا. اختر نطاقا اصغر")
        return {str(year) for year in range(start, end + 1)}

    years = set(extract_years(value))
    if years:
        return years

    raise ValueError("صيغة السنة غير صالحة. مثال صحيح: 2024 او 2022-2024")


def fetch_page(session, url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        time.sleep(random.uniform(1, 2))
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except requests.RequestException as e:
            if attempt == max_retries:
                log.error(f"فشل في تحميل الصفحة: {url} -> {e}")
                return None
            log.warning(f"اعادة المحاولة ({attempt}/{max_retries}) لتحميل: {url}")


def get_subjects(session, level_code):
    url = f"{BASE_URL}/ar/{level_code}"
    soup = fetch_page(session, url)
    if not soup:
        return []
    subjects = []
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        prefix = f"/ar/{level_code}/"
        if href.startswith(prefix) and href.count("/") == 3:
            slug = href.split("/")[-1]
            name = link.get_text(strip=True).split("عدد")[0].strip()
            if name and slug and slug not in ("moyenne", "youtube"):
                subjects.append({"name": name, "slug": slug})
    seen = set()
    unique = []
    for s in subjects:
        if s["slug"] not in seen:
            seen.add(s["slug"])
            unique.append(s)
    return unique


def get_categories(session, level_code, subject_slug):
    url = f"{BASE_URL}/ar/{level_code}/{subject_slug}"
    soup = fetch_page(session, url)
    if not soup:
        return []
    categories = []
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        prefix = f"/ar/{level_code}/{subject_slug}/"
        if href.startswith(prefix) and href.count("/") == 4:
            code = href.split("/")[-1]
            name = link.get_text(strip=True)
            count_part = name.split("\n")[0].strip() if "\n" in name else ""
            display_name = name
            for part in name.split("\n"):
                part = part.strip()
                if part and not part.isdigit():
                    display_name = part
                    break
            if code and code not in ("moyenne", "youtube"):
                categories.append({"name": display_name, "code": code})
    seen = set()
    unique = []
    for c in categories:
        if c["code"] not in seen:
            seen.add(c["code"])
            unique.append(c)

    # Some subjects (for example BEM/BAC variants) expose exams directly on the
    # subject page without an intermediate category URL.
    if not unique:
        has_direct_cards = bool(
            soup.select("a.btn-item-sujet, a.btn-item, a[class*='btn-item'][data-id]")
        )
        if has_direct_cards:
            unique.append({"name": "All exams", "code": "direct"})

    return unique


def get_exam_links(session, level_code, subject_slug, category_code, year_filter=None, limit=None):
    if category_code in (None, "", "direct"):
        url = f"{BASE_URL}/ar/{level_code}/{subject_slug}"
    else:
        url = f"{BASE_URL}/ar/{level_code}/{subject_slug}/{category_code}"
    soup = fetch_page(session, url)
    if not soup:
        return []

    try:
        allowed_years = normalize_year_filter(year_filter)
    except ValueError as exc:
        log.error(str(exc))
        return []

    exams = []
    seen_urls = set()
    cards = soup.select("a.btn-item-sujet, a.btn-item, a[class*='btn-item'][data-id]")
    for card in cards:
        href = card.get("href", "")
        data_id = card.get("data-id", "")

        full_url = None
        if href and "/sujets/" in href:
            full_url = _to_absolute_url(href)
        elif data_id:
            decoded = decode_data_id(data_id)
            if decoded:
                full_url = f"{BASE_URL}/ar/sujets/{decoded}"

        if not full_url:
            continue

        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        text = card.get_text(" ", strip=True)
        title_attr = card.get("title", "")
        combined_text = f"{title_attr} {text}".strip()
        years = extract_years(combined_text)
        year = years[0] if years else None

        if allowed_years and not set(years).intersection(allowed_years):
            continue

        has_solution = any(keyword in combined_text.lower() for keyword in ("✅", "تصحيح", "الحل", "solution"))

        title = title_attr.strip() or text
        title = re.sub(r"\s+", " ", title)
        if len(title) > 120:
            title = title[:120].strip()

        exams.append({
            "title": title,
            "url": full_url,
            "year": year,
            "years": years,
            "has_solution": has_solution,
        })

        if limit and len(exams) >= limit:
            break

    return exams


def get_pdf_url(session, exam_url):
    soup = fetch_page(session, exam_url)
    if not soup:
        return None

    selectors = [
        "a#actions-download[href]",
        "a[href$='.pdf']",
        "a[href*='.pdf?']",
        "a[href*='/download']",
    ]

    for selector in selectors:
        for link in soup.select(selector):
            href = link.get("href", "")
            absolute = _to_absolute_url(href)
            if absolute:
                return absolute

    return None
