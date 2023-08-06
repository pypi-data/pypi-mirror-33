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

import os

from sqlalchemy.engine import url


def make_db_uri(config):
    # sqlite is special, screw that
    if config['DB_ENGINE'].startswith('sqlite'):
        host = config['DB_HOST'] or ':memory:'
        sep = os.path.sep * 3
        return 'sqlite:%s%s' % (sep, host)

    params = {
        'drivername': config['DB_ENGINE'],
        'host': config['DB_HOST'],
    }

    if config['DB_USER']:
        params['username'] = config['DB_USER']

    if config['DB_PASSWORD']:
        params['password'] = config['DB_PASSWORD']

    if config['DB_NAME']:
        params['database'] = config['DB_NAME']

    if config['DB_PORT']:
        params['port'] = int(config['DB_PORT'])

    return url.URL(**params)
