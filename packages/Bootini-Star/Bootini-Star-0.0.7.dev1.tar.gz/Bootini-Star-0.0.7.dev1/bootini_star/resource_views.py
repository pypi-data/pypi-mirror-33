"""
Views for resources like favicons, images, etc.
"""
__author__ = 'Ralph Seichter'

from flask import Blueprint, redirect, url_for
from flask.views import MethodView
from werkzeug.routing import BaseConverter


class StaticFileConverter(BaseConverter):

    def __init__(self, url_map, *groups):
        super().__init__(url_map)
        self.regex = groups[0]


class StaticFile(MethodView):
    methods = ['GET']

    @staticmethod
    def get(filename):
        return redirect(url_for('static', filename=filename))


blueprint = Blueprint('res', __name__)
blueprint.add_url_rule(
    "/<static(r'\S+\.(?:ico|png|svg|webmanifest|xml)'):filename>",
    view_func=StaticFile.as_view('static'))
