"""
Callback view for EVE SSO.
"""
__author__ = 'Ralph Seichter'

import flask_login
import oauthlib
from flask import Blueprint, redirect, request, url_for
from flask.helpers import flash
from flask.views import MethodView
from flask_login import current_user
from pymongo.errors import OperationFailure

from .extensions import log
from .models import Character
from .sso import EveSso


class Callback(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self):
        es = EveSso()
        # noinspection PyBroadException,PyPep8
        try:
            auth_token = es.auth_token(request.args.get('code'))
        except oauthlib.oauth2.OAuth2Error as e:
            log.error(f'Error obtaining authentication token: {e}')
            flash('Error obtaining authentication token.', 'danger')
            return redirect(url_for('bs.dashboard'))
        """
        The rest of this method is not covered by automated unit tests because
        it would require user interaction to authorise a character.
        """
        resp = es.auth_verify()
        if resp.ok:  # pragma: no cover
            json = resp.json()
            character = Character()
            character.eve_id = json['CharacterID']
            character.name = json['CharacterName']
            character.token = auth_token
            _list = current_user.characters
            if _list:
                _list.append(character)
            else:
                _list = [character]
            current_user.characters = _list
            try:
                if current_user.update() == 1:
                    log.info(
                        f'User {current_user.email} added character {character.eve_id}')
                    flash('Verification successful.', 'success')
                    return redirect(url_for('bs.dashboard'))
            except OperationFailure as e:
                log.error(f'Error saving user data: {e}')
        flash('Verification failed.', 'error')
        return redirect(url_for('bs.index'))


blueprint = Blueprint('sso', __name__)
blueprint.add_url_rule('/sso/callback', view_func=Callback.as_view('callback'))
