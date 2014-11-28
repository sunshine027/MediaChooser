# Django settings for demo project.  
import os
import logging
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ROOT = os.path.abspath(os.path.split(__file__)[0])

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'mc-test1'             # Or path to database file if using sqlite3.
DATABASE_USER = 'mediachooser'             # Not used with sqlite3.
DATABASE_PASSWORD = 'choosermedia'         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Harbin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/lhh/MediaChooser/mc_media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://211.94.190.88/media-lhh-dev-ad/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7b^j@h&)wj6c^wo$heb5&m(o4@d-f-s9(%!y(^m%xq4fg11@ud'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    #'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'MediaChooser.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/lhh/MediaChooser/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'registration',
    'MediaChooser.ad',
    #'MediaChooser.audience',
    'MediaChooser.client',
    #'MediaChooser.history_data',
    'MediaChooser.media',
    'MediaChooser.misc',
    'MediaChooser.media_weekly_report',
    'MediaChooser.ad_resource_mgmt',
    'MediaChooser.media_planning',
    'MediaChooser.NielsenMedia',
    'MediaChooser.user_behaviour',
    'MediaChooser.pr',
)

REDIRECT_FIELD_NAME = 'next'
LOGIN_URL = '/lhh-dev-ad/accounts/login/'
LOGIN_REDIRECT_URL = '/lhh-dev-ad/'

DEFAULT_CHARSET = 'utf-8'
LANGUAGE_CODE = 'utf-8'

FORCE_SCRIPT_NAME = '/lhh-dev-ad'
SCRIPT_URL = '/lhh-dev-ad'
REDIRECT_URL = '/lhh-dev-ad'

# setting for clicks from DE
CLICK_COMPENSATION_COEFFICIENT = 1

# dir for store uploaded media planning file
UPLOADED_MP_DIR = '/home/lhh/backup/uploaded-mp/'

# The number of click, above that can be regarded as useful
USEFUL_CLICK_NUMBER = 10

# log file to track actions like updating, importing, refreshing
MP_INFO_CHANGE_LOG = '/home/lhh/log/mp-change/'

# time span to find unuploaded mp
MP_SEARCH_SPAN = 30

# Related to mail
EMAIL_HOST = 'mail.and-c.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'andc-it'
EMAIL_HOST_PASSWORD = 'ludaifei'

# logging config
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(message)s',
    filename = 'log/mc-visit.log',
    )