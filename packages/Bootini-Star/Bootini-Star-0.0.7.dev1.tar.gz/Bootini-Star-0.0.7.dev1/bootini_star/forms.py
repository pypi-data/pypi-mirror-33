"""
Flask forms for logging in and signing up.
"""
__author__ = 'Ralph Seichter'

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

CPW_LABEL = 'Confirm password'
CPW_MSG = 'Password confirmation is required.'
CREATE_INDEXES = 'Create MongoDB indexes'
CURRENT_LABEL = 'Current password'
CURRENT_MSG = 'Current password is required.'
EMAIL_LABEL = 'Email address'
EMAIL_MSG = 'Valid email address is required.'
MATCH_MSG = 'Password and confirmation must match.'
PW_LABEL = 'Password'
PW_MSG = 'Password is required.'


class ChangePasswordForm(FlaskForm):
    current = PasswordField(CURRENT_LABEL, validators=[
        DataRequired(CURRENT_MSG)])
    password = PasswordField(PW_LABEL, validators=[DataRequired(PW_MSG)])
    confirm = PasswordField(CPW_LABEL, validators=[
        DataRequired(CPW_MSG),
        EqualTo('password', message=MATCH_MSG)
    ])
    submit = SubmitField('Change password')


class LoginForm(FlaskForm):
    email = StringField(EMAIL_LABEL, validators=[Email(message=EMAIL_MSG)])
    password = PasswordField(PW_LABEL, validators=[DataRequired(PW_MSG)])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    email = StringField(EMAIL_LABEL, validators=[Email(message=EMAIL_MSG)])
    password = PasswordField(PW_LABEL, validators=[DataRequired(PW_MSG)])
    confirm = PasswordField(CPW_LABEL, validators=[
        DataRequired(CPW_MSG),
        EqualTo('password', message=MATCH_MSG)
    ])
    submit = SubmitField('Sign me up')


class SelfDestructForm(FlaskForm):
    email = StringField(EMAIL_LABEL, validators=[Email(message=EMAIL_MSG)])
    password = PasswordField(PW_LABEL, validators=[DataRequired(PW_MSG)])


class AdminForm(FlaskForm):
    submit = SubmitField(CREATE_INDEXES)
