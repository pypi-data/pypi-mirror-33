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

import json

from wtforms import Field
from wtforms.widgets import TextInput

class CommaSeparatedListField(Field):
    widget = TextInput()

    def __init__(self, label='', validators='', coerce=None, strip=True, **kw):
        self.coerce = coerce
        self.strip = strip
        super().__init__(label, validators, **kw)

    def _value(self):
        if self.data:
            return ', '.join(str(d) for d in self.data)
        return ''

    def process_formdata(self, val):
        self.data = []
        if not val:
            return

        l = val[0].split(',')
        for v in l:
            if self.strip:
                v = v.strip()
            if self.coerce:
                v = self.coerce(v)
            if v:
                self.data.append(v)
