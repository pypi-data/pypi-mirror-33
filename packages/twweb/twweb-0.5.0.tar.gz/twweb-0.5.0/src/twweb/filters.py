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


def strip(val):
    if val and isinstance(val, str):
        return val.strip()
    return val


def strip_all(chars):
    trans_table = {ord(ch): None for ch in chars}
    def _f(val):
        if val and isinstance(val, str):
            return val.translate(trans_table)
        return val
    return _f


def falsey_as_none(val):
    if not val:
        return None
    return val
