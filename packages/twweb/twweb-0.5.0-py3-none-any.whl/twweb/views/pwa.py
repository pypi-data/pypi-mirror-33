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


from flask import Blueprint

from .view_utils import (twweb_template)
pwa_view = Blueprint('pwa', __name__)

@pwa_view.route('/offline')
def offline():
    msg = 'TWWeb currently works in offline mode and cannot access this page. '\
          'To continue, check your internet connection.'
    return twweb_template('error.html',
                          title='Offline mode',
                          error=msg)
