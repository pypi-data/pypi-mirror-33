TWWeb is `Taskwarrior's <https://taskwarrior.org>`__ web interface.

It's aimed to be run on a internet-facing web server by a single user (it
currently supports only a single registered user and a single taskrc).

Installation
============

To install TWWeb you'll need a web server able to run Python applications.
You'll also need a database, but sqlite should be fine as TWWeb doesn't store a
lot. Obviously you'll also need a working Taskwarrior.

We'll install all required components inside a virtualenv. Before you start, you
should select and create a directory in which TWWeb will be placed. For now
we'll assume ``/var/www/example.com/twweb``, where "example.com" part is
typically replaced with a name of your domain.

::

    $ sudo mkdir -p /var/www/example.com/twweb
    $ sudo chown $USER:www-data /var/www/example.com/twweb
    $ chmod 775 /var/www/example.com/twweb
    $ cd /var/www/example.com/twweb

Above commands create and set appropriate permissions for TWWeb's directory.
When following this installation method, TWWeb itself will need write
permissions in this directory so that's why we change the group permission to
``rwx``.

Taskwarrior configuration
-------------------------

For Taskwarrior, choose the most appropriate installation method for your
server. Keep in mind that you'll need a ``task`` executable which will be
available in ``$PATH`` of a user which will run TWWeb (typically ``www-data``).

For example, for Debian-based distributions the following command should do the
trick:

::

    $ sudo apt install task

Now create a separate taskrc and task directory in which Taskwarrior will store
its data:

::

    $ mkdir -m 775 task && chown $USER:www-data task
    $ echo "data.location=`pwd`/task" > taskrc

If you want to use synchronization with Task Server, you can place your
certificates in this directory and configure it inside a newly created
``taskrc`` file.

Installation with uWSGI
-----------------------

Now we'll install TWWeb and uWSGI inside a new virtualenv:

::

    $ virtualenv -p python3 venv
    $ venv/bin/pip install twweb uwsgi
    $ inst=`find venv -name twweb -type d`

The last command saves the path to the directory in which TWWeb package is
located. It's not strictly required, but will become handy later.  Typically it
will be found in a directory like ``venv/lib/python3.5/site-packages/twweb``.

Inside ``utils`` directory in Git repository there are various example
configuration files. One of them is ``twweb-uwsgi.ini`` which is a configuration
for uwsgi. You can edit it to your likings, but the original one should work
fine as well. Copy it to your current directory.

Now we'll create TWWeb's configuration file, named ``twweb.cfg``. We'll add a
custom ``SECRET_KEY`` and ``PIN`` to it (*VERY IMPORTANT*). We'll also point
sqlite database to our directory and taskrc to the previously created one:

::

    SECRET_KEY = 'this should be secret and complex'
    PIN = 'additional password used for first register'

    DB_ENGINE = 'sqlite'
    DB_HOST = '/var/www/example.com/twweb/twweb.db'

    TW_TASKRC = '/var/www/example.com/twweb/taskrc'

You have to point to it via ``TWWEB_SETTINGS`` environment variable, for example
this way:

::

    $ export TWWEB_SETTINGS=`pwd`/twweb.cfg

And that's it! You can run TWWeb with ``venv/bin/uwsgi --ini twweb-uwsgi.ini``.
Logs are stored inside ``/var/log/uwsgi/twweb.log``.

Now you'll have to configure your web server (e.g. Apache or Nginx) to forward
all requests to your uwsgi app. For example for Nginx you can add something like
that:

::

    location /update {
      include uwsgi_params;
      uwsgi_pass unix:/run/uwsgi/twweb.socket
    }
