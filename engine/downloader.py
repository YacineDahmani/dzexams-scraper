import os
import re
import time
import random
from pathlib import Path

import requests
from tqdm import tqdm
from utils.logger import log


DOWNLOADS_DIR = Path("downloads")


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name, max_length=140):
    # Remove characters that are invalid on Windows and normalize whitespace.
    sanitized = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", str(name))
    sanitized = re.sub(r"\s+", " ", sanitized).strip().strip(".")
    if not sanitized:
        sanitized = "document"
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip(" .")
    return sanitized


def download_pdf(session, url, dest_folder, filename=None, max_retries=3):
    if not filename:
        filename = url.split("/")[-1].split("?")[0] or "document"
    filename = sanitize_filename(filename)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    dest_folder = Path(dest_folder)
    ensure_dir(dest_folder)
    filepath = dest_folder / filename
    temp_filepath = filepath.with_suffix(filepath.suffix + ".part")

    if filepath.exists():
        log.info(f"File already exists: {filename}")
        return str(filepath)

    for attempt in range(1, max_retries + 1):
        try:
            with session.get(url, stream=True, timeout=45) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))

                with open(temp_filepath, "wb") as f:
                    with tqdm(total=total, unit="B", unit_scale=True, desc=filename[:40], ncols=80) as bar:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if not chunk:
                                continue
                            f.write(chunk)
                            bar.update(len(chunk))

            os.replace(temp_filepath, filepath)

            log.info(f"Downloaded: {filename}")
            return str(filepath)

        except requests.Timeout:
            if temp_filepath.exists():
                os.remove(temp_filepath)
            if attempt == max_retries:
                log.error(f"Connection timed out while downloading {filename}")
                return None
            log.warning(f"Connection timeout. Retrying ({attempt}/{max_retries}) for: {filename}")
            time.sleep(random.uniform(1, 2))

        except requests.RequestException as e:
            if temp_filepath.exists():
                os.remove(temp_filepath)
            if attempt == max_retries:
                log.error(f"Failed to download {filename} due to network issue: {e}")
                return None
            log.warning(f"Network issue. Retrying ({attempt}/{max_retries}) for: {filename}")
            time.sleep(random.uniform(1, 2))

        except OSError as e:
            if temp_filepath.exists():
                os.remove(temp_filepath)
            log.error(f"Failed to save file {filename}: {e}")
            return None

        except Exception as e:
            if temp_filepath.exists():
                os.remove(temp_filepath)
            if attempt == max_retries:
                log.error(f"Failed to download {filename}: {e}")
                return None
            log.warning(f"Retrying ({attempt}/{max_retries}) for: {filename}")
            time.sleep(random.uniform(1, 2))


def build_dest_folder(level_code, subject_slug, category_code):
    return DOWNLOADS_DIR / level_code / subject_slug / category_code
