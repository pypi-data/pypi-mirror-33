"""
Support classes for sending email to application users.
"""
__author__ = 'Ralph Seichter'

import re
import smtplib
from email.message import EmailMessage
from email.utils import localtime
from urllib.parse import urlparse
from uuid import uuid4

from .extensions import app_config, log

UNITTEST_DOMAIN = '@unittest.unittest'


def unittest_address(local_part: str) -> str:
    return local_part + UNITTEST_DOMAIN


def is_unittest_address(address: str) -> bool:
    return address and address.endswith(UNITTEST_DOMAIN)


class _Mail:
    pat = re.compile(r'\w@[\w-]{2,}\.\w{2,}')

    def _parse_config(self):
        u = urlparse(app_config['SMTP_SERVER_URI'])
        if u.scheme not in ['smtp', 'tls']:
            raise ValueError('SMTP_SERVER_URI missing or scheme unknown')
        self.scheme = u.scheme
        self.host = u.hostname
        if u.port:
            self.port = u.port
        else:
            self.port = 587 if u.scheme == 'tls' else 25
        if u.path:
            self.username = re.sub(r'^/(.+)', r'\1', u.path)
            self.password = u.query
        else:
            self.username = None
        self.address = app_config['SMTP_SENDER_ADDRESS']
        if re.search(self.pat, self.address):
            return
        raise ValueError('SMTP_SENDER_ADDRESS missing or malformed')

    def send(self, headers, body):
        self._parse_config()
        log.debug('SMTP host is ' + self.host + ':' + str(self.port))
        if self.username:
            log.debug('SMTP username is ' + self.username)
        headers['Date'] = localtime()
        headers['Message-ID'] = str(uuid4()) + '@Bootini-Star'
        em = EmailMessage()
        for k, v in headers.items():
            em[k] = v
        em.set_content(body)
        with smtplib.SMTP(self.host, self.port) as smtp:
            if self.username:
                smtp.starttls()
                smtp.login(self.username, self.password)
            recipient = headers['To'] if 'To' in headers else None
            if is_unittest_address(recipient):
                log.debug(f'Skipping mail to {recipient}')
            else:
                smtp.send_message(em)


class RegistrationMail(_Mail):

    def send(self, headers, url):
        headers['Subject'] = 'Your Bootini Star account has been created'
        body = (
            'Somebody (hopefully you) registered your email address with a'
            '\nBootini Star account. To activate your account, please click'
            '\nthe following link:\n\n'
        )
        super().send(headers, body + url)
