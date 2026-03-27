import unittest
import re

from engine.downloader import sanitize_filename
from engine.parser import decode_data_id, extract_years, normalize_year_filter


class ParserUtilsTests(unittest.TestCase):
    def test_decode_data_id_returns_subject_slug(self):
        encoded = "W3NwXF5ydDtsTzlKWzhWXVZPPV1rclpeVlBiSllcOEE="
        decoded = decode_data_id(encoded)
        self.assertIsNotNone(decoded)
        self.assertTrue(len(decoded) > 20)
        self.assertRegex(decoded, r"^[A-Za-z0-9+/=]+$")

    def test_extract_years_with_mixed_text(self):
        text = "موضوع 2023/2024 مع التصحيح 2024"
        self.assertEqual(extract_years(text), ["2023", "2024"])

    def test_normalize_year_filter_single_year(self):
        self.assertEqual(normalize_year_filter("2024"), {"2024"})

    def test_normalize_year_filter_range(self):
        self.assertEqual(normalize_year_filter("2022-2024"), {"2022", "2023", "2024"})

    def test_normalize_year_filter_invalid(self):
        with self.assertRaises(ValueError):
            normalize_year_filter("abcd")


class DownloaderUtilsTests(unittest.TestCase):
    def test_sanitize_filename_removes_forbidden_characters(self):
        raw = 'topic<>:"/\\|?* exam.pdf'
        clean = sanitize_filename(raw)
        self.assertNotIn("<", clean)
        self.assertNotIn(">", clean)
        self.assertNotIn(":", clean)
        self.assertNotIn("/", clean)
        self.assertNotIn("\\", clean)
        self.assertNotIn("|", clean)
        self.assertNotIn("?", clean)
        self.assertNotIn("*", clean)


if __name__ == "__main__":
    unittest.main()
