"""
Application views/routes are based on Flask's MethodView. All primary views are
combined into a Flask blueprint.
"""
__author__ = 'Ralph Seichter'

import datetime
from operator import attrgetter

import flask_login
from flask import Blueprint, flash, redirect, url_for
from flask.templating import render_template
from flask.views import MethodView, View
from flask_login.utils import current_user
from pymongo.errors import OperationFailure

import swagger_client
from bootini_star import esi
from bootini_star.esi import Cache, EveGroup, EveType
from bootini_star.forms import AdminForm
from swagger_client.rest import ApiException
from .extensions import app_config, log
from .models import User, create_unique_index
from .sso import EveSso

ADMIN_REQUIRED = 'Admin privileges are required.'
eveCache = esi.IdNameCache()


class RenderTemplate(View):

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        return render_template(self.template, config=app_config)


def flash_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'danger')


class Dashboard(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self):
        auth_url, auth_state = EveSso().auth_url_state()
        cu: User = current_user
        characters = sorted(cu.characters,
                            key=attrgetter('name')) if cu.characters else None
        return render_template(
            'dashboard.html',
            characters=characters,
            auth_url=auth_url,
            auth_state=auth_state,
            config=app_config
        )


class Character(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id):
        api = swagger_client.CharacterApi()
        try:
            return render_template(
                'character.html',
                character=esi.get_character(api, character_id)
            )
        except ApiException as e:
            return api_fail(e)


def refresh_token(api, character: Character):
    es = EveSso(character.token)
    rt = es.refresh_token()
    if rt.token_changed:
        log.debug(f'Updating token for character {character.eve_id}')
        character.token = rt.token
        character.modified_at = datetime.datetime.utcnow()
        if current_user.update() != 1:
            log.error(
                f'Error updating token for character {character.eve_id}')
    client = api.api_client
    client.set_default_header('User-Agent', app_config['USER_AGENT'])
    client.configuration.access_token = rt.token['access_token']
    return api


def mail_api(current_character):
    return refresh_token(swagger_client.MailApi(), current_character)


def skills_api(current_character):
    return refresh_token(swagger_client.SkillsApi(), current_character)


def api_fail(api_exception):
    flash('EVE Swagger Interface call failed: ' +
          api_exception.reason + '.', 'danger')
    return redirect(url_for('.index'))


class MailList(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id, label=None):
        cc = current_user.get_character(character_id)
        if cc:  # pragma: no cover (Needs live character)
            api = mail_api(cc)
            kwargs = {'labels': [label]} if isinstance(label, int) else {}
            try:
                labels = esi.get_mail_labels(api, character_id)
                mails = esi.get_mails(api, character_id, **kwargs)
                mail_ids = {m._from for m in mails}
                eveCache.eve_characters(mail_ids)
            except ApiException as e:
                return api_fail(e)
            sl = sorted(labels.labels, key=attrgetter('label_id'))
            sm = sorted(mails, key=attrgetter('timestamp'), reverse=True)
            return render_template('maillist.html', eveCache=eveCache,
                                   character_id=character_id, labels=sl,
                                   maillist=sm)
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class Mail(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id: int, mail_id: int):
        cc = current_user.get_character(character_id)
        if cc:
            api = mail_api(cc)
            try:
                rv = api.get_characters_character_id_mail_mail_id(
                    character_id, mail_id)
                return render_template('mail.html', character_id=character_id,
                                       mail_id=mail_id, eveCache=eveCache,
                                       mail=rv)
            except ApiException as e:
                return api_fail(e)
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class MarkMailRead(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id: int, mail_id: int, read: int):
        cc = current_user.get_character(character_id)
        if cc:  # pragma: no cover (Needs live character)
            api = mail_api(cc)
            try:
                status = 'read' if read else 'unread'
                esi.mark_mail_read(api, character_id, mail_id, read)
                flash(f'Mail has been marked as {status}.', 'success')
            except ApiException as e:
                return api_fail(e)
            return redirect(url_for('.maillist', character_id=character_id))
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class RemoveMail(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id: int, mail_id: int):
        cc = current_user.get_character(character_id)
        if cc:  # pragma: no cover (Needs live character)
            api = mail_api(cc)
            try:
                api.delete_characters_character_id_mail_mail_id(
                    character_id, mail_id)
                flash('Mail has been deleted.', 'success')
            except ApiException as e:
                return api_fail(e)
            return redirect(url_for('.maillist', character_id=character_id))
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class RemoveCharacter(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id):
        try:
            log.debug(f'Remove character {character_id}')
            current_user.remove_character(character_id)
            if current_user.update() == 1:
                flash(f'Character {character_id} was removed.', 'success')
            else:
                log.warning(f'Character {character_id} could not be removed')
                flash(f'Character {character_id} could not be removed.',
                      'danger')
        except OperationFailure as e:
            log.error(f'Error removing character: {e}')
            flash(f'Character {character_id} could not be removed.', 'danger')
        return redirect(url_for('.dashboard'))


class Skills(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id):
        cc = current_user.get_character(character_id)
        if cc:  # pragma: no cover (Needs live character)
            api = skills_api(cc)
            try:
                rv = api.get_characters_character_id_skillqueue(character_id)
                return render_template('skillqueue.html', eveCache=eveCache,
                                       character_id=character_id,
                                       skillq=sorted(rv, key=attrgetter(
                                           'queue_position')))
            except ApiException as e:
                return api_fail(e)
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class Skill(MethodView):
    methods = ['GET']

    @staticmethod
    def get(skill_id):
        skill = eveCache.eve_type(skill_id)
        return render_template('skill.html', skill=skill)


class Admin(MethodView):
    methods = ['GET', 'POST']

    @flask_login.fresh_login_required
    def get(self):
        if current_user.is_admin:
            return render_template('quickform.html', form=AdminForm())
        flash(ADMIN_REQUIRED, 'warning')
        return redirect(url_for('.login'))

    @flask_login.fresh_login_required
    def post(self):
        if current_user.is_admin:
            create_unique_index(Cache().collection, 'eve_id')
            create_unique_index(EveGroup().collection, 'eve_id')
            create_unique_index(EveType().collection, 'eve_id')
            create_unique_index(User().collection, 'email')
            flash('Created database indexes.', 'success')
            return redirect(url_for('.dashboard'))
        flash(ADMIN_REQUIRED, 'warning')
        return redirect(url_for('.login'))


blueprint = Blueprint('bs', __name__)
blueprint.add_url_rule(
    '/', view_func=RenderTemplate.as_view('index', template='index.html'))
blueprint.add_url_rule('/admin', view_func=Admin.as_view('admin'))
blueprint.add_url_rule('/dashboard', view_func=Dashboard.as_view('dashboard'))
blueprint.add_url_rule('/dashboard/rm/<int:character_id>',
                       view_func=RemoveCharacter.as_view('rmcharacter'))
blueprint.add_url_rule('/character/<int:character_id>',
                       view_func=Character.as_view('character'))
blueprint.add_url_rule(
    '/mail/<int:character_id>/<int:mail_id>', view_func=Mail.as_view('mail'))
blueprint.add_url_rule('/mail/rm/<int:character_id>/<int:mail_id>',
                       view_func=RemoveMail.as_view('rmmail'))
blueprint.add_url_rule('/mail/rd/<int:character_id>/<int:mail_id>/<int:read>',
                       view_func=MarkMailRead.as_view('mailread'))
blueprint.add_url_rule('/maillist/<int:character_id>/<int:label>',
                       view_func=MailList.as_view('maillabel'))
blueprint.add_url_rule('/maillist/<int:character_id>',
                       view_func=MailList.as_view('maillist'))
blueprint.add_url_rule('/skill/<int:skill_id>',
                       view_func=Skill.as_view('skill'))
blueprint.add_url_rule('/skillqueue/<int:character_id>',
                       view_func=Skills.as_view('skillqueue'))
