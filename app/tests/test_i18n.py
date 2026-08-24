from django.test import TestCase


class I18nRoutingTests(TestCase):
    def test_default_redirects_to_prefixed(self):
        resp = self.client.get("/")
        self.assertIn(resp.status_code, (302, 301))
        self.assertTrue(resp["Location"].startswith(("/en", "/az", "/ru", "/tr")))

    def test_en_home_renders(self):
        resp = self.client.get("/en/")
        self.assertEqual(resp.status_code, 200)

    def test_each_language_home_renders(self):
        for lang in ("en", "az", "ru", "tr"):
            resp = self.client.get(f"/{lang}/")
            self.assertEqual(resp.status_code, 200, lang)
