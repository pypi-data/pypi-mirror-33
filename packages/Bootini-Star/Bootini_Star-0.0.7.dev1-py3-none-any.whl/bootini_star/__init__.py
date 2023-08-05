"""
Inspect EVE Online in-game mail and skill queues in a web browser. Inspired by
CCP's discontinued EVE Gate app.

This project was started on 2018-04-20 by Ralph Seichter.
"""
__author__ = 'Ralph Seichter'

import logging
import os
import re
from datetime import datetime

from flask import Flask
from flask_bootstrap import Bootstrap

from .account_views import add_account_url_rules
from .extensions import app_config, log, login_manager
from .resource_views import StaticFileConverter, blueprint as res_blueprint
from .sso_views import blueprint as sso_blueprint
from .views import blueprint as bs_blueprint

app = Flask(__name__)
# Development configuration settings are the default.
app_settings = os.getenv('APP_SETTINGS', 'bootini_star.config.Development')
app.config.from_object(app_settings)
app_config.update(app.config)

# Set logging level
level_str = app_config['LOG_LEVEL'].upper()
level = getattr(logging, level_str, None)
if not isinstance(level, int):
    raise ValueError(f'Invalid LOG_LEVEL {level_str}')
log.setLevel(level)

Bootstrap(app)

login_manager.init_app(app)
login_manager.login_message_category = 'info'
login_manager.blueprint_login_views = {
    bs_blueprint.name: 'bs.login',
    sso_blueprint.name: 'bs.login'
}

app.url_map.converters['static'] = StaticFileConverter
add_account_url_rules(bs_blueprint)
app.register_blueprint(bs_blueprint)
app.register_blueprint(res_blueprint)
app.register_blueprint(sso_blueprint)

_re_flags = re.RegexFlag.MULTILINE
_div_pat = re.compile(r'<div>(.*?)</div>', flags=_re_flags)
_font_pat = re.compile(r'<(font[^>]*|/font)>', flags=_re_flags)
_span_pat = re.compile(r'<(span[^>]*|/span)>', flags=_re_flags)
_datetime_pat = re.compile(r'(\d{4}\-\d{2}\-\d{2}).(\d{2}:\d{2})')
_time_pat = re.compile(r'\+00:00')
_si_pat = re.compile(r'href="showinfo:(\d+)//(\d+)"', flags=_re_flags)


@app.template_filter('eve_html')
def html_filter(html: str) -> str:
    """
    Strip selected HTML tags created within EVE's mail client.

    :param html: HTML string to clean up
    """
    html = re.sub(_font_pat, '', html)
    html = re.sub(_span_pat, '', html)
    return re.sub(_div_pat, r'\1', html)


@app.template_filter('showinfo')
def showinfo_filter(html: str, urlbase: str) -> str:
    """
    Convert EVE 'showinfo' links into HTML links. This currently only works for
    links that reference EVE characters, other link types are ignored.

    :param html: HTML string to parse
    :param urlbase: Base URL to append to
    """
    flags = _re_flags
    pos = 0
    m = _si_pat.search(html)
    while m:
        if 1373 <= int(m.group(1)) <= 1386:
            href = f'href="{urlbase}character/{m.group(2)}"'
            html = re.sub(m.group(0), href, html, flags=flags)
        pos += len(m.group(0))
        m = _si_pat.search(html, pos)
    return html


@app.template_filter('eve_time')
def time_filter(dt) -> str:
    """
    Returns a string representation of a datetime object. Seconds, microseconds
    and TZ offset (EVE uses UTC anyway) are truncated.

    :param dt: Datetime object to convert to a string.
    """
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M')
    m = _datetime_pat.search(dt)
    if m:
        return f'{m[1]} {m[2]}'
    return dt
