import requests
from django.conf import settings

from ievv_opensource.ievv_sms import sms_registry


class Backend(sms_registry.AbstractSmsBackend):
    """
    A pswin (https://pswin.com) backend.

    To use this backend, you should set the following Django settings:

    - ``PSWIN_USERNAME``: The pswin username (USER).
    - ``PSWIN_PASSWORD``: The pswin password (PWD).
    - ``PSWIN_SENDER``: The pswin sender (SND).
    - ``PSWIN_DEFAULT_COUNTRY_CODE``: The country code to use if received
      phone numbers do not start with ``+<code>`` or ``00<code>``.
      E.g.: 47 for norway.

    If you do not set these settings, you must include
    them as kwargs each time you send a message, and this
    makes it hard to switch SMS sending provider.

    The backend_id for this backend is ``pswin``.
    """
    @classmethod
    def get_backend_id(cls):
        return 'pswin'

    def __init__(self, phone_number, message,
                 pswin_sender=None,
                 pswin_username=None,
                 pswin_password=None,
                 pswin_default_country_code=None,
                 **kwargs):
        self._pswin_sender = pswin_sender
        self._pswin_username = pswin_username
        self._pswin_password = pswin_password
        self._pswin_default_country_code = pswin_default_country_code
        super().__init__(phone_number=phone_number, message=message, **kwargs)

    @property
    def pswin_base_url(self):
        return 'https://simple.pswin.com'

    @property
    def pswin_username(self):
        return self._pswin_username or settings.PSWIN_USERNAME

    @property
    def pswin_password(self):
        return self._pswin_password or settings.PSWIN_PASSWORD

    @property
    def pswin_sender(self):
        return self._pswin_sender or settings.PSWIN_SENDER

    @property
    def default_country_code(self):
        return self._pswin_default_country_code or settings.PSWIN_DEFAULT_COUNTRY_CODE

    def clean_phone_number(self, phone_number):
        phone_number = self.STRIP_WHITESPACE_PATTERN.sub('', phone_number)
        if phone_number.startswith('00'):
            phone_number = phone_number[2:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        else:
            phone_number = '{}{}'.format(self.default_country_code, phone_number)
        return phone_number

    @property
    def pswin_postdata(self):
        return {
            'USER': self.pswin_username,
            'PW': self.pswin_password,
            'RCV': self.cleaned_phone_number,
            'SND': self.pswin_sender,
            'TXT': self.cleaned_message.encode('ISO-8859-1'),
            'Content-Type': 'text/html; ISO-8859-1'
        }

    def send(self):
        """
        Send the message using pswin.
        """
        requests.post(self.pswin_base_url, params=self.pswin_postdata)
