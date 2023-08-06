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

from flask import current_app as app
from wtforms.validators import ValidationError

from twweb.model import User

class Forbidden:
    def __init__(self, message=None):
        if not message:
            message = 'This field must be empty.'
        self.message = message

    def __call__(self, form, field):
        if bool(field.data):
            raise ValidationError(self.message)


class MaxOneUser:
    def __init__(self, message=None):
        if not message:
            message = 'Only one registered user is allowed.'
        self.message = message

    def __call__(self, form, field):
        if User.query.scalar():
            raise ValidationError(self.message)


class PinCheck():
    def __init__(self, message=None):
        if not message:
            message = 'Incorrect PIN'
        self.message = message

    def __call__(self, form, field):
        pin = app.config.get('PIN')
        if pin and field.data != pin:
            raise ValidationError(self.message)
