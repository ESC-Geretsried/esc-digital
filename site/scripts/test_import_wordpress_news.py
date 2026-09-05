#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from import_wordpress_news import ContentSanitizer, is_flash, slugify


class WordPressImportTests(unittest.TestCase):
    def test_flash_news_is_excluded_by_category_or_title(self):
        self.assertTrue(is_flash({"categories": [4], "title": {"rendered": "Saison"}}, {4: "Flash-News"}))
        self.assertTrue(is_flash({"categories": [], "title": {"rendered": "Flashnews: Test"}}, {}))
        self.assertFalse(is_flash({"categories": [4], "title": {"rendered": "Spielbericht"}}, {4: "River Rats"}))

    def test_slugify_is_stable_and_safe(self):
        self.assertEqual(slugify("Vorbereitungsspiele der River Rats"), "vorbereitungsspiele-der-river-rats")
        self.assertEqual(slugify("Ärger & Spaß"), "rger-spass")

    def test_sanitizer_removes_active_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parser = ContentSanitizer(root, root, {})
            parser.feed('<p>Text <strong>wichtig</strong></p><script>alert(1)</script><iframe src="x"></iframe>')
            self.assertEqual(parser.html(), "<p>Text <strong>wichtig</strong></p>")


if __name__ == "__main__":
    unittest.main()
