import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import build


class SitemapDates(unittest.TestCase):
    def test_verified_dates_only(self):
        site = build.read_data()['site']
        for path in ('/gravel-calculator/', '/mulch-calculator/'):
            entry = ET.fromstring(build.sitemap_url_entry(site, path))
            self.assertEqual(entry.findtext('lastmod'), '2026-10-26')
            self.assertEqual(entry.findtext('loc'), 'https://nscalculators.com' + path)
        area = ET.fromstring(build.sitemap_url_entry(site, '/area-calculator/'))
        self.assertEqual(area.findtext('lastmod'), '2026-10-25')
        self.assertNotIn('lastmod', build.sitemap_url_entry(site, '/mortgage-calculator/'))
        with patch.dict(build.SITEMAP_LASTMOD, {'/gravel-calculator/': 'invalid'}):
            with self.assertRaises(ValueError):
                build.sitemap_url_entry(site, '/gravel-calculator/')
