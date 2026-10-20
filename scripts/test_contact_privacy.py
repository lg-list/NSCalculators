import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class ContactPrivacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.info_pages(build.read_data()["site"])

    def test_contact_warns_that_reports_are_public(self):
        html = self.pages["/contact/"]
        self.assertIn("Reports and replies are visible to other people", html)
        self.assertIn("A GitHub account is required to submit", html)
        self.assertIn("Use made-up or anonymized example values", html)
        self.assertIn("without private query parameters", html)
        self.assertNotIn("the values you entered, the result you expected", html)
        self.assertNotIn("For corrections, feedback, privacy questions", html)

    def test_private_channel_is_not_fabricated(self):
        for slug in ("/contact/", "/privacy-policy/"):
            with self.subTest(slug=slug):
                html = self.pages[slug]
                self.assertIn("A private contact channel is not currently published", html)
                self.assertNotIn("mailto:", html)
        self.assertIn('href="/contact/"', self.pages["/privacy-policy/"])
        self.assertIn('href="/privacy-policy/"', self.pages["/contact/"])

    def test_repository_template_warns_before_requesting_inputs(self):
        template = (build.ROOT / ".github" / "ISSUE_TEMPLATE" / "calculator-correction.md").read_text(encoding="utf-8")
        self.assertTrue(template.startswith("---\nname: Calculator correction\n"))
        self.assertLess(template.index("## Public report warning"), template.index("## Steps and anonymous example inputs"))
        self.assertIn("This issue and its replies will be public", template)
        self.assertIn("Do not post an email address or phone number", template)
        self.assertIn("Use invented or anonymized numbers", template)
        self.assertIn("I checked that this report", template)


if __name__ == "__main__":
    unittest.main()
