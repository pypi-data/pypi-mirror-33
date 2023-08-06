from django import test

from ievv_opensource.ievv_sms.backends import pswin


@test.override_settings(PSWIN_DEFAULT_COUNTRY_CODE='47')
class TestBackend(test.TestCase):
    def test_clean_phone_number__no_country_code(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number('12345678'),
            '4712345678')

    def test_clean_phone_number__plus_country_code(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number('+9912345678'),
            '9912345678')

    def test_clean_phone_number__00_country_code(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number('009912345678'),
            '9912345678')

    def test_clean_phone_number__whitespace(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number(' 123 45 678 '),
            '4712345678')
