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

from collections import OrderedDict

from flask import current_app as app
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, Markup, session)
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFError
from wtforms.validators import InputRequired, AnyOf
from taskw.exceptions import TaskwarriorError

from twweb.forms import (TaskForm, TaskActionForm, LoginForm, RegistrationForm,
                         ActionForm)
from twweb.validators import Forbidden
from twweb.model import db, User, login_manager

from .view_utils import (no_cache, session_save_form, session_load_form,
                          session_clear_form, twweb_template)

task_view = Blueprint('task', __name__)

class TaskGroup:
    def __init__(self):
        self.pending = []
        self.waiting = []
        self.completed = []
        self.other = []

    def __len__(self):
        return len(self.pending)


def form_errors(form):
    for e in form.errors:
        yield '%s: %s' % (e.capitalize(), '\n'.join(form.errors[e]))


def stringify_filter(flt, *, init=None):
    s = init if init else ''
    multi_keys = app.config['TW_KEYS_HAS_CHECK']

    for key, value in flt.items():
        if key in multi_keys:
            for elem in value.split(','):
                s += ' %s.has:%s' % (key, elem.strip())
        else:
            s += ' %s:%s' % (key, value)
    s = s.strip()

    if s:
        return '(%s)' % s
    return ''


def sort(tasks, key, order_name='asc'):
    def _get(key, default=None):
        def _f(dct):
            return dct.get(key, default)
        return _f

    rev = (order_name == 'desc')
    tasks.sort(key=_get(key, ''), reverse=rev)


def limit(tasks, no):
    tasks[:] = tasks[:no]


def postprocess(tasks, actions):
    if 'sort' in actions:
        sort(tasks, actions['sort'], actions.get('ord', 'desc'))
    if 'limit' in actions:
        limit(tasks, int(actions['limit']))


def split_filters():
    actions_names = ('sort', 'ord', 'view', 'limit')
    args = request.args.copy()

    actions = {}

    for an in actions_names:
        if an in args:
            actions[an] = args[an]
            del args[an]

    return args, actions


def uuids(id_list):
    if not id_list:
        return []
    query = ','.join(str(id_) for id_ in id_list if id_ > 0)
    tasks = app.tw._get_task_objects(query , 'export')
    return [t['uuid'] for t in tasks]


def ids(uuid_list):
    if not uuid_list:
        return []
    query = ' or '.join(str('uuid:%s' % u) for u in uuid_list)
    tasks = app.tw._get_task_objects(query , 'export')
    return [t['id'] for t in tasks if t['id']]


def change_task_status(task, status):
    def _completed(task, _):
        app.tw.task_done(uuid=task['uuid'])

    def _delete(task, _):
        app.tw.task_delete(uuid=task['uuid'])

    def _other(task, status):
        task['status'] = status.strip()
        app.tw.task_update(task)

    routines = {'completed': _completed, 'delete': _delete}
    changer = routines.get(status, _other)

    if not task:
        flash('Task doesn\'t exist.', 'error')
        return False

    try:
        changer(task, status)
    except TaskwarriorError as e:
        flash(e.stderr.decode('utf-8'), 'error')
        return False
    except ValueError as e:
        flash(str(e), 'error')
        return False

    return True


def add_get(form):
    session_load_form(form)
    return twweb_template('edit.html', form=form, title='New Task')


def add_post(form):
    form.uuid.validators.insert(0, Forbidden())
    form.description.validators.insert(0, InputRequired())

    session_save_form(form)

    if form.validate():
        discard_fields = ('csrf_token')
        data = form.data
        dct = {name: data[name]
               for name in data
               if name not in discard_fields and data[name]}

        # Due to usability reasons, user is required to provide task ids.
        # Furthermore, only task with ids (i.e. pending ones) can actually block
        # any task, so it makes more sense than providing anything else. But TW
        # requires uuids here, so here we are.
        if 'depends' in dct:
            dct['depends'] = uuids(dct['depends'])

        task = app.tw.task_add(**dct)
        msg = 'Created a new task: <a href="%s">%d</a>' % \
            (url_for('task.task', uuid=task['uuid']), task['id'])
        messages = [('success', Markup(msg))]
        session_clear_form(form)
    else:
        messages = [('error', e) for e in form_errors(form)]

    return twweb_template('edit.html', messages=messages, form=form,
                          title="New Task")


@task_view.route('/add', methods=['GET', 'POST'])
@login_required
@no_cache
def add():
    form = TaskForm(request.form)
    f = globals()['add_%s' % request.method.lower()]
    return f(form)


def edit_post(uuid):
    task = app.tw.get_task(uuid=uuid)[1]
    messages = []

    form = TaskForm()

    form.uuid.validators.insert(0, Forbidden())
    form.description.validators.insert(0, InputRequired())

    if form.validate():
        # Most of these fields don't exist in form, but maybe in future some of
        # them will (as e.g. hidden input)
        discard_fields = ('csrf_token', 'next', 'id', 'uuid', 'modified',
                          'entry')
        data = form.data
        dct = {name: data[name]
               for name in data
               if name not in discard_fields}

        if 'depends' in dct:
            dct['depends'] = uuids(dct['depends'])

        # update dict, task is saved below
        task.update(dct)

        try:
            up = app.tw.task_update(task)[1]
        except TaskwarriorError as e:
            messages.append(('error', e.stderr.decode('utf-8')))
        else:
            msg = 'Task <a href="%s">%d</a> successfully updated.' % \
                (url_for('task.task', uuid=up['uuid']), up['id'])
            flash(Markup(msg), 'success')
            return form.redirect()

    for e in form_errors(form):
        messages.append(('error', e))

    return twweb_template('edit.html', form=form, title='Edit Task',
                          messages=messages)


def edit_get(uuid):
    task = app.tw.get_task(uuid=uuid)[1]
    if not task:
        flash('Requested task does not exist.', 'error')
        return redirect(url_for('task.add'), code=302)

    if 'depends' in task:
        task['depends'] = ids(task['depends'])

    form = TaskForm(None, data=task, next=request.referrer)
    return twweb_template('edit.html', form=form, task=task,
                          title='Edit Task')


@task_view.route('/edit/<uuid>', methods=['GET', 'POST'])
@login_required
@no_cache
def edit(uuid):
    f = globals()['edit_%s' % request.method.lower()]
    return f(uuid)


@task_view.route('/complete', methods=['POST'],
                 defaults={'status': 'completed'},
                 endpoint='complete')
@task_view.route('/delete', methods=['POST'],
                 defaults={'status': 'deleted'},
                 endpoint='delete')
@task_view.route('/change_status', methods=['POST'], defaults={'status': None})
@login_required
def change_status(status):
    '''A common method of changing task status. User can mark task as completed
    and deleted. Generic `change_status` route exists for undoing purposes.'''
    form = TaskActionForm()

    if status is None:
        form.param.validators = [InputRequired(),
                                 AnyOf(['pending', 'deleted', 'completed',
                                        'waiting', 'recurring'])]
        status = form.param.data
    else:
        # For /complete and /delete routes only one status value is allowed, so
        # we'll block setting it via a param field.
        form.param.validators = [Forbidden()]

    if form.validate():
        task = app.tw.get_task(uuid=form.uuid.data)[1]
        if not task:
            flash('Incorrect UUID: %s' % form.uuid.data, 'error')
        else:
            prev_status = task['status']
            if change_task_status(task, status):
                red = form.next.data or url_for('task.task', uuid=task['uuid'])
                rendered_form = TaskActionForm(
                    formdata=None,
                    uuid=str(task['uuid']),
                    param=prev_status,
                    next=red)

                undo_html = render_template(
                    'form-action.html',
                    action='task.change_status',
                    label='Undo',
                    text='Task changed to %s.' % status,
                    form=rendered_form)
                flash(Markup(undo_html), 'success')
    else:
        for e in form_errors(form):
            flash(e, 'error')

    return form.redirect()


@task_view.route('/annotate', methods=['POST'])
@login_required
def annotate():
    form = TaskActionForm()
    form.param.validators = [InputRequired()]
    if form.validate():
        task = app.tw.get_task(uuid=form.uuid.data)[1]
        if not task:
            flash('Incorrect UUID: %s' % form.uuid.data, 'error')
        else:
            ann = form.param.data.strip()
            try:
                app.tw.task_annotate(task, ann)
            except TaskwarriorError as e:
                flash(e.stderr.decode('utf-8'), 'error')
            else:
                flash('Annotation added', 'success')
    else:
        for e in form_errors(form):
            flash(e, 'error')

    return form.redirect()


@task_view.route('/task/<uuid>', methods=['GET'])
@login_required
def task(uuid):
    task = app.tw.get_task(uuid=uuid)[1]
    messages = []
    if not task:
        messages = messages.append(('error', 'No task for UUID %s' % str(uuid)))

    return twweb_template('task.html', task=task, messages=messages,
                          title='Task details',
                          udas=app.tw.config['uda'])


@task_view.route('/tasks', methods=['GET'])
@login_required
def tasks():
    filters, actions = split_filters()
    messages = []

    allowed_views = ['table', 'cards']
    templ = actions.get('view', session.get('view', allowed_views[0]))
    session['view'] = templ
    if templ not in allowed_views:
        flash('Invalid view: %s' % templ, 'warning')
        args = request.args.copy()
        del args['view']
        return redirect(url_for('.tasks', **args))

    custom = None
    if 'filter' in filters:
        custom = filters['filter']
        del filters['filter']  # don't stringify it

    tasks = []

    try:
        query = stringify_filter(filters, init=custom)
        if query:
            # XXX: we use a private interface of taskw here. I don't know why
            # they wouldn't provide users a possibility to run any taskwarrior
            # command.
            tasks = app.tw._get_task_objects(query, 'export')
        else:
            tasks = app.tw._get_task_objects('export')

    except TaskwarriorError as e:
        messages.append(('error', e.stderr.decode('utf-8')))
        messages.append(('error', 'Errorneous query: %s' % query))
    else:
        postprocess(tasks, actions)

        if not tasks:
            messages.append(('warning',
                             'No tasks fulfill requested query: %s' % query))

    return twweb_template('%s.html' % templ, title='Tasks',
                          tasks=tasks, messages=messages)


@task_view.route('/projects', methods=['GET'])
@login_required
def projects():
    tasks = app.tw.filter_tasks({'project.any': '', 'status': 'pending'})

    projects = sorted(set(t['project'] for t in tasks))
    project_tasks = app.tw.filter_tasks({
        'or': [('project', pr) for pr in projects]
    })

    groups = OrderedDict((pr, TaskGroup()) for pr in projects)
    for t in project_tasks:
        prname = t['project']
        if t['status'] == 'pending':
            groups[prname].pending.append(t)
        elif t['status'] == 'waiting':
            groups[prname].waiting.append(t)
        elif t['status'] == 'completed':
            groups[prname].completed.append(t)
        elif t['status'] != 'deleted':
            groups[prname].other.append(t)

    return twweb_template('accordion.html',
                          title='Active projects',
                          groups=groups)


@task_view.route('/tags', methods=['GET'])
@login_required
def tags():
    tasks = app.tw.filter_tasks({'tags.any': '', 'status': 'pending'})

    tags_set = set()
    for t in tasks:
        tags_set.update(t['tags'])

    tags = sorted(tags_set)
    tag_tasks = app.tw.filter_tasks({
        'or': [('tags.any', tag) for tag in tags]
    })

    groups = OrderedDict((tag, TaskGroup()) for tag in tags)

    def _add_task_to_tag_groups(task, group):
        for tag in task['tags']:
            try:
                getattr(groups[tag], group).append(task)
            except KeyError:  # task is inactive and has additional tag
                continue

    for t in tag_tasks:
        if t['status'] == 'pending':
            _add_task_to_tag_groups(t, 'pending')
        elif t['status'] == 'waiting':
            _add_task_to_tag_groups(t, 'waiting')
        elif t['status'] == 'completed':
            _add_task_to_tag_groups(t, 'completed')
        elif t['status'] != 'deleted':
            _add_task_to_tag_groups(t, 'other')

    return twweb_template('accordion.html',
                          title='Active tags',
                          groups=groups)


@task_view.route('/sync', methods=['POST'])
@login_required
def sync():
    form = ActionForm()
    if form.validate():
        app.tw.sync()
        flash('Tasks synchronized', 'success')
    else:
        for e in form_errors(form):
            flash(e, 'error')
    return form.redirect()

@task_view.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You\'ve been logged out.', 'success')
    return redirect(url_for('.index'))


@task_view.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate():
        login_user(form.user, remember=form.remember.data)
        session_clear_form(form)
        return form.redirect('.tasks', status='pending')

    flash('Invalid credentials', 'error')
    session_save_form(form)
    return redirect(url_for('.index'))


@task_view.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if not form.validate():
        for e in form_errors(form):
            flash(e, 'error')
        session_save_form(form)
        return redirect(url_for('.index'))

    user = User(username=form.username.data, password=form.password.data)
    db.session.add(user)
    db.session.commit()

    flash('New account for %s successfully created' % form.username.data,
          'success')
    session_clear_form(form)
    return redirect(url_for('.index'))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You are not authorized to see this page. Please login first.',
          'error')
    return redirect(url_for('.index'))


@task_view.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    return twweb_template('error.html',
                           title='Invalid CSRF token',
                           error=e.description), 400


@task_view.app_errorhandler(404)
def handle_page_not_found(e):
    return twweb_template('error.html',
                           title='404: Page not found',
                           error='Requested page doesn\'t exist.'), 404


@task_view.route('/', methods=['GET'])
@no_cache
def index():
    if current_user.is_authenticated:
        return redirect(url_for('task.tasks', status='pending'), code=302)
    lf = LoginForm(None)
    rf = RegistrationForm(None)

    session_load_form(lf)
    session_load_form(rf)

    return twweb_template('index.html', login_form=lf, register_form=rf)
