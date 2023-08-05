"""
Configuration for development, testing and production environments is handled
using different objects. These objects inspect environment variables. Settings
should be overridden by using these env variables.
"""
__author__ = 'Ralph Seichter'

import os
import socket

from bootini_star import version

BAD = 'bad'
DEFAULT_DEVELOPMENT_DB_URI = 'mongodb://127.0.0.1/bs'
DEFAULT_TESTING_DB_URI = DEFAULT_DEVELOPMENT_DB_URI + '_test'
DEFAULT_ESI_CALLBACK_URI = 'http://127.0.0.1:5000/sso/callback'


class Config:
    """
    Configuration object base class.

    If you need to change settings like ESI_CALLBACK_URI to address
    local requirements, use environment variables.
    """
    VERSION = version.__version__
    USER_AGENT = version.USER_AGENT
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    SMTP_SERVER_URI = os.getenv('SMTP_SERVER_URI', '')
    SMTP_SENDER_ADDRESS = os.getenv('SMTP_SENDER_ADDRESS', '')
    SECRET_KEY = os.getenv('SECRET_KEY', BAD)
    ESI_CLIENT_ID = os.getenv('ESI_CLIENT_ID', BAD)
    ESI_SECRET_KEY = os.getenv('ESI_SECRET_KEY', BAD)
    ESI_CALLBACK_URI = os.getenv('ESI_CALLBACK_URI', DEFAULT_ESI_CALLBACK_URI)
    OAUTH_BASE = 'https://login.eveonline.com/oauth/'
    ESI_AUTHORIZATION_URI = OAUTH_BASE + 'authorize'
    ESI_TOKEN_URI = OAUTH_BASE + 'token'
    ESI_VERIFY_URI = OAUTH_BASE + 'verify'


class Development(Config):
    DEBUG = True
    TESTING = False
    MONGODB_URI = os.getenv('MONGODB_URI', DEFAULT_DEVELOPMENT_DB_URI)


class Testing(Config):
    DEBUG = True
    TESTING = True
    MONGODB_URI = os.getenv('MONGODB_URI', DEFAULT_TESTING_DB_URI)
    """Testing requires SERVER_NAME for request independent URL generation."""
    SERVER_NAME = os.getenv('SERVER_NAME', socket.getfqdn())
    """Disable CSRF protection for WTForms during testing."""
    WTF_CSRF_ENABLED = False


class Production(Config):
    DEBUG = False
    TESTING = False
    MONGODB_URI = os.getenv('MONGODB_URI')
