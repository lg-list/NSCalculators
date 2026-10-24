import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class AnalyticsContextTests(unittest.TestCase):
    def test_tag_uses_explicit_context_without_changing_stream(self):
        with patch.object(build, 'GA4_MEASUREMENT_ID', 'G-TESTONLY'):
            tag = build.google_tag()
        self.assertEqual(tag.count('https://www.googletagmanager.com/gtag/js?id='), 1)
        self.assertIn("gtag('set', northstarAnalyticsContext)", tag)
        self.assertIn("gtag('config', \"G-TESTONLY\", northstarAnalyticsContext)", tag)
        self.assertNotIn('location.search', tag)
        self.assertNotIn('location.hash', tag)

    def test_disabled_analytics_stays_disabled(self):
        with patch.object(build, 'GA4_MEASUREMENT_ID', ''):
            self.assertEqual(build.google_tag(), '')


if __name__ == '__main__':
    unittest.main()
