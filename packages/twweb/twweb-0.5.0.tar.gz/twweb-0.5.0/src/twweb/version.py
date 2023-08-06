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
 
from pkg_resources import get_distribution, DistributionNotFound

__appname__ = "TWWeb"
__author__ = "Michał Góral"
__license__ = "GNU GPL 3"
__website__ = "https://gitlab.com/mgoral/twweb"

try:
    __version__ = get_distribution(__appname__.lower()).version
except DistributionNotFound:
    __version__ = '0.x.x-not-installed'
