# Copyright (C) 2018 Michał Góral.
#
# This file is part of TWWeb
#
# TWWeb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWWeb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWWeb. If not, see <http://www.gnu.org/licenses/>.

import uuid
import json
from urllib.parse import urlparse, urljoin

from flask import redirect, abort, request, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField, DateTimeField, IntegerField, SelectField,
                     HiddenField, PasswordField, BooleanField)
from wtforms.validators import InputRequired, UUID, Optional, NumberRange, URL
from wtforms.widgets import TextInput, Input, HiddenInput

from twweb.filters import strip, strip_all, falsey_as_none
from twweb.validators import MaxOneUser, PinCheck
from twweb.fields import CommaSeparatedListField
from twweb.model import User
from twweb.security import pwd_context


def _DateTimeField(*a, **kw):
    kw.setdefault('format', '%Y-%m-%d')
    kw['widget'] = Input(input_type='date')
    return DateTimeField(*a, **kw)



def _is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def _get_redirect_target():
    sources = [request.referrer]
    for s in sources:
        if not s:
            continue
        return s


class _SessionMixin:
    @property
    def session_fields(self):
        return set()


class RedirectForm(FlaskForm, _SessionMixin):
    next = StringField(
        'next',
        widget=HiddenInput(),
        validators=[Optional()])  # TODO: URL validator

    def redirect(self, endpoint=None, **kw):
        '''Handles redirects. The order in which possible redirects are checked
        is following:
        1. Redirect stored inside 'next' field (e.g. via formdata or data)
        2. (fallback) Redirect given as the endpoint to redirect() method
        3. (fallback) Redirect deduced from the other sources.'''
        red = self.next.data
        fallback = url_for(endpoint, **kw) if endpoint \
                                           else _get_redirect_target()

        for url in [red, fallback]:
            if url and _is_safe_url(url):
                return redirect(urljoin(request.host_url, url), code=302)
        return abort(404)


class TaskForm(RedirectForm):
    uuid = StringField('uuid',
        filters=[strip],
        validators=[
            Optional(),
            UUID()])

    description = StringField('description',
        description='Task description',
        filters=[strip_all('\r\n')],
        validators=[Optional()])

    tags = CommaSeparatedListField('tags',
        description='List of tags',
        validators=[Optional()])

    project = StringField('project',
        description='Task\'s project',
        validators=[Optional()])

    priority = SelectField('priority',
        description='Task\'s priority',
        default='',
        choices=[('', ''), ('H', 'H'), ('M', 'M'), ('L', 'L')],
        validators=[Optional()],
        filters=[falsey_as_none])

    due = _DateTimeField('due',
        description='Task\'s due date',
        validators=[Optional()])
    recur = StringField('recur',
        description='Task\'s recurrence pattern',
        validators=[Optional()])
    until = _DateTimeField('until',
            description='',
            validators=[Optional()])
    wait = _DateTimeField('wait',
            description='Task\'s waiting date',
            validators=[Optional()])
    scheduled = _DateTimeField('scheduled',
                description='Task\'s schedule date',
                validators=[Optional()])

    depends = CommaSeparatedListField('depends',
        description='IDs of other tasks',
        validators=[Optional()],
        coerce=int)

    @property
    def session_fields(self):
        return set(['uuid', 'description', 'tags', 'project', 'priority', 'due',
                    'recur', 'until', 'wait', 'scheduled'])


class TaskActionForm(RedirectForm):
    uuid = StringField(
        'uuid',
        widget=HiddenInput(),
        validators=[
            InputRequired(),
            UUID()])

    param = StringField(
        'param',
        widget=HiddenInput(),
        validators=[Optional()])


class LoginForm(RedirectForm):
    def __init__(self, *a, **kw):
        kw.setdefault('prefix', 'login')
        super().__init__(*a, **kw)

    username = StringField(
        'username',
        validators=[InputRequired()])

    password = PasswordField('password')

    remember = BooleanField('remember')

    @property
    def session_fields(self):
        return set(['username'])

    def validate(self):
        if not super().validate():
            return False

        try:
            user = User.query.filter_by(username=self.username.data).one()
        except:
            self.username.errors.append('Invalid credentials')
            return False

        if not pwd_context.verify(self.password.data, user.password):
            self.username.errors.append('Invalid credentials')
            return False

        self.user = user
        return True


class RegistrationForm(RedirectForm):
    def __init__(self, *a, **kw):
        kw.setdefault('prefix', 'registration')
        super().__init__(*a, **kw)

    username = StringField(
        'username',
        validators=[MaxOneUser(), InputRequired()])

    password = PasswordField('password')

    pin = StringField(
        'pin',
        validators=[PinCheck()])

    @property
    def session_fields(self):
        return set(['username'])


class ActionForm(RedirectForm):
    pass
