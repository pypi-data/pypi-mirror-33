# This is default configuration for TWWeb
# If you edit this, keep in mind that it WILL be used on a production servers.

DB_ENGINE = 'sqlite' # engine name
DB_HOST = 'twweb.sqlite' # host or path for sqlite. If empty for sqlite, represents :memory:
DB_PORT = '' # port number
DB_NAME = '' # database name
DB_USER = '' # database username
DB_PASSWORD = '' # database user's password

SECRET_KEY = None
PIN = None

TW_TASKRC = '' # path to existing alternate Taskwarrior's configuration file.

WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None
