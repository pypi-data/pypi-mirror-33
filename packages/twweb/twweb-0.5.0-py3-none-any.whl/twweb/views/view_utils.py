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

from functools import wraps

from flask import make_response, session, render_template, request


def no_cache(view):
    @wraps(view)
    def _f(*a, **kw):
        resp = make_response(view(*a, **kw))
        resp.headers['Cache-Control'] = 'no-cache, no-store, max-age=0, \
                                        must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = 'Sat, 26 Jul 1997 01:00:00 GMT'
        return resp
    return _f


def session_save_form(form):
    form_name = form.__class__.__name__
    for field in form.session_fields:
        entry = '%s_%s' % (form_name, field)
        session[entry] = getattr(form, field).data


def session_load_form(form):
    form_name = form.__class__.__name__
    for field in form.session_fields:
        entry = '%s_%s' % (form_name, field)
        val = session.get(entry)
        if val and not getattr(form, field).data:
            getattr(form, field).data = val


def session_clear_form(form):
    form_name = form.__class__.__name__
    for field in form.session_fields:
        entry = '%s_%s' % (form_name, field)
        try:
            del session[entry]
        except KeyError:
            pass


def twweb_template(templ, **kw):
    def _page_vars(kw):
        ret = dict(
            title=kw.pop('title', None),
            id=kw.pop('id', request.endpoint),
            messages=kw.pop('messages', []),
        )
        return ret

    pv = _page_vars(kw)
    return render_template(templ, page=pv, **kw)
