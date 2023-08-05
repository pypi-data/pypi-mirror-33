"""
Handle EVE SSO calls.
"""
__author__ = 'Ralph Seichter'

from collections import namedtuple
from datetime import datetime

from requests_oauthlib import OAuth2Session

from .config import Config
from .extensions import log

scope = [
    'esi-characters.read_standings.v1',
    'esi-mail.organize_mail.v1',
    'esi-mail.read_mail.v1',
    'esi-mail.send_mail.v1',
    'esi-skills.read_skillqueue.v1',
]

RefreshToken = namedtuple('RefreshToken', ['token', 'token_changed'])


class EveSso(OAuth2Session):
    """
    Some code in this class is not covered by automated unit tests because it
    would require user interaction to authorize a character using EVE SSO.
    """
    config = Config()
    # Required when refreshing by CCP's ESI
    refresh_kwargs = {
        'client_id': config.ESI_CLIENT_ID,
        'client_secret': config.ESI_SECRET_KEY
    }

    def __init__(self, token_dict=None):
        super().__init__(
            client_id=self.config.ESI_CLIENT_ID,
            redirect_uri=self.config.ESI_CALLBACK_URI,
            auto_refresh_url=self.config.ESI_TOKEN_URI,
            auto_refresh_kwargs=self.refresh_kwargs,
            scope=scope,
            token=token_dict
        )

    def auth_url_state(self, state=None):
        url, state = self.authorization_url(
            self.config.ESI_AUTHORIZATION_URI,
            state=state
        )
        return url, state

    def auth_token(self, code):
        self.token = self.fetch_token(
            self.config.ESI_TOKEN_URI,
            client_secret=self.config.ESI_SECRET_KEY,
            code=code
        )
        return self.token

    def auth_verify(self):
        return self.get(self.config.ESI_VERIFY_URI)

    # noinspection PyMethodOverriding
    def refresh_token(self, refresh=False) -> RefreshToken:
        if not refresh:
            ea = self.token.get('expires_at')
            if ea and datetime.utcnow() > datetime.utcfromtimestamp(ea - 90):
                log.debug('Access token expired')
                refresh = True
        if refresh:
            log.debug('Attempting to refresh token')
            token = super().refresh_token(
                self.config.ESI_TOKEN_URI,
                **self.refresh_kwargs
            )
            log.debug('Returning refreshed token')
            return RefreshToken(token=token, token_changed=True)
        log.debug('Returning existing token')
        return RefreshToken(token=self.token, token_changed=False)
