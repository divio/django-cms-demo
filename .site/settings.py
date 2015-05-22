# -*- coding: utf-8 -*-
import os
import dj_database_url
import django_cache_url
from getenv import env
import json

gettext = lambda s: s

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_ROOT = os.path.join(PROJECT_DIR, 'data')

TEMPLATE_DEBUG = DEBUG = False

MANAGERS = ADMINS = ()

LANGUAGES = [('en', 'en')]
DEFAULT_LANGUAGE = 0

TIME_ZONE = 'Europe/Zurich'

LANGUAGE_CODE = 'en'

SITE_ID = 1

USE_L10N = USE_I18N = True


MEDIA_ROOT = os.path.join(DATA_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(DATA_ROOT, 'static_collected')
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# WARN: these are all overwritten from settings.json! (I think)
TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'sekizai.context_processors.sekizai',
    'cms.context_processors.cms_settings',
    'cmscloud.context_processors.boilerplate',
    'cmscloud.context_processors.debug',
    'aldryn_snake.template_api.template_processor',
]

CMS_TEMPLATES = [
    ('main.html', 'Full width'),
    ('main_sidebar.html', 'Sidebar right'),
    ('sidebar_main.html', 'Sidebar left'),
]

ROOT_URLCONF = 'urls'

CMSCLOUD_STATIC_URL = 'https://static.aldryn.com/'

TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIR, 'cmscloud/templates'),
    os.path.join(PROJECT_DIR, 'templates'),
    os.path.join(PROJECT_DIR, 'custom_templates'),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # 'py.warnings': {
        #     'handlers': ['console'],
        # },
    }
}

###############################################################################
# Cloud user authentication
###############################################################################

# User can change its data on Login's server.
# We cannot do a sync of "recently changed" user data due to these reasons:
# - security risk, leaking user data to unauthorized websites,
# - it would require some periodic tasks (celery?),
# - stage websites are being paused during which the sync wouldn't work
CLOUD_USER_SESSION_EXPIRATION = 24 * 60 * 60  # 24h = 1day

###############################################################################
# Sync changed files
###############################################################################
SYNC_CHANGED_FILES_SIGNATURE_MAX_AGE = 60  # 60sec


settings_json_filename = os.path.join(os.path.dirname(__file__), 'settings.json')
if os.path.exists(settings_json_filename):
    with open(settings_json_filename) as fobj:
        try:
            locals().update(json.load(fobj))
        except ValueError as e:
            print e

if env('DATABASE_URL'):
    if 'DATABASES' not in locals():
        DATABASES = {}
    DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))

DOMAIN = env('DOMAIN', locals().get('DOMAIN', None))
DOMAIN_ALIASES = env('DOMAIN_ALIASES', locals().get('DOMAIN_ALIASES', ''))
DOMAIN_REDIRECTS = env('DOMAIN_REDIRECTS', locals().get('DOMAIN_REDIRECTS', ''))
if DOMAIN:
    ALDRYN_SITES_DOMAINS = {
        1: {
            'domain': DOMAIN,
            'aliases': [d.strip() for d in DOMAIN_ALIASES.split(',') if d.strip()],
            'redirects': [d.strip() for d in DOMAIN_REDIRECTS.split(',') if d.strip()]
        }
    }

# all strings are unicode after loading from json. But some settings MUST BE STRINGS
if isinstance(locals().get('EMAIL_HOST_PASSWORD', None), unicode):
    EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD.encode('ascii')

cache_url = env('CACHE_URL', locals().get('CACHE_URL', None))
if cache_url is not None:
    if 'CACHES' not in locals():
        CACHES = {}
    CACHES['default'] = django_cache_url.parse(cache_url)

if 'CMS_LANGUAGES' in locals():
    # convert site_ids that are strings instead of ints to ints
    CMS_LANGUAGES = {
        int(key) if isinstance(key, basestring) and key.isdigit() else key: value
        for key, value in CMS_LANGUAGES.items()
    }

PARLER_LANGUAGES = {}
for site_id, languages in CMS_LANGUAGES.items():
    if isinstance(site_id, int):
        langs = [{'code': lang['code']} for lang in languages]
        PARLER_LANGUAGES.update({site_id: langs})
parler_defaults = {'fallback': LANGUAGE_CODE}
for k, v in CMS_LANGUAGES.get('default', {}).items():
    if k in ['hide_untranslated', ]:
        parler_defaults.update({k: v})
PARLER_LANGUAGES.update({'default': parler_defaults})

templates_json_filename = os.path.join(os.path.dirname(__file__), 'cms_templates.json')
if os.path.exists(templates_json_filename):
    with open(templates_json_filename) as fobj:
        try:
            locals()['CMS_TEMPLATES'] = json.load(fobj)
        except ValueError as e:
            print e


if 'DATABASES' not in locals() or 'DATABASES' in locals() and 'default' not in DATABASES:
    localname = os.environ.get("LOCAL_DATABASE_NAME", ":memory:")
    print "USING IN %s SQLITE3" % localname
    print "NO DATABASE CONFIGURED!!! USING %s SQLITE3 DATABASE!!!"
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': localname,
        }
    }

# TODO: remove django-filer stuff from here. It should be an addon.
THUMBNAIL_QUALITY = 90
# THUMBNAIL_HIGH_RESOLUTION = False  # FIXME: enabling THUMBNAIL_HIGH_RESOLUTION causes timeouts/500!
THUMBNAIL_PRESERVE_EXTENSIONS = ['png', 'gif']
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)
THUMBNAIL_SOURCE_GENERATORS = (
    'easy_thumbnails.source_generators.pil_image',
)
THUMBNAIL_CACHE_DIMENSIONS = True
FILER_IMAGE_USE_ICON = True
for app in ['filer', 'easy_thumbnails', 'mptt', 'polymorphic', 'cmsplugin_filer_file', 'cmsplugin_filer_image']:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)
FILER_DEBUG = True
FILER_ENABLE_LOGGING = True
# end filer


# Compress is not working well with multiple docker containers that don't have a shared filesystem.
COMPRESS_ENABLED = env('COMPRESS_ENABLED', False)


# extra INSTALLED_APPS
EXTRA_INSTALLED_APPS = [
    'aldryn_sites',
    'aldryn_boilerplates',
    'reversion',
    'parler',
    'hvad',
    'robots',
    # TODO: remove all plugins from here. they should be addons
    'djangocms_text_ckeditor',
    # 'cms.plugins.picture',  # now using django-filer
    'djangocms_link',  # 'cms.plugins.link',
    'django_select2',  # required by djangocms-link
    # 'cms.plugins.file',  # now using django-filer
    'djangocms_snippet',  # 'cms.plugins.snippet',
    'djangocms_googlemap',  # 'cms.plugins.googlemap',
    'django.contrib.sitemaps',
    'captcha',
    'treebeard',
    'mptt',
]
for app in EXTRA_INSTALLED_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)


# extra MIDDLEWARE_CLASSES
EXTRA_MIDDLEWARE_CLASSES = [
    'cmscloud.middleware.CurrentSiteMiddleware',
    'cmscloud.middleware.AldrynUserMiddleware',
]
for middleware in EXTRA_MIDDLEWARE_CLASSES:
    if middleware not in MIDDLEWARE_CLASSES:
        MIDDLEWARE_CLASSES.append(middleware)
# aldryn-sites middleware should be near the top
MIDDLEWARE_CLASSES.insert(0, 'aldryn_sites.middleware.SiteMiddleware')


# extra TEMPLATE_CONTEXT_PROCESSORS
EXTRA_TEMPLATE_CONTEXT_PROCESSORS = [
    'aldryn_boilerplates.context_processors.boilerplate',
]
for context_processor in EXTRA_TEMPLATE_CONTEXT_PROCESSORS:
    if context_processor not in TEMPLATE_CONTEXT_PROCESSORS:
        TEMPLATE_CONTEXT_PROCESSORS.append(context_processor)

# in this django-cms version there is no 'cms.context_processors.media' anymore
# instead we should use 'cms.context_processors.cms_settings'.
# This hack has to be here, because TEMPLATE_CONTEXT_PROCESSORS is generated on
# controlpanel for all versions of the base project. It should really be defined in the
# base project though.
TEMPLATE_CONTEXT_PROCESSORS[TEMPLATE_CONTEXT_PROCESSORS.index('cms.context_processors.media')] = 'cms.context_processors.cms_settings'


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    # important! place right before django.contrib.staticfiles.finders.AppDirectoriesFinder
    'aldryn_boilerplates.staticfile_finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    # important! place right before django.template.loaders.app_directories.Loader
    'aldryn_boilerplates.template_loaders.AppDirectoriesLoader',
    'django.template.loaders.app_directories.Loader',
]



# TODO: move this to ckeditor addon aldyn config when we extract it from the base project
# boilerplate should provide /static/js/modules/ckeditor.wysiwyg.js and /static/css/base.css
CKEDITOR_SETTINGS = {
    'height': 300,
    'language': '{{ language }}',
    'toolbar': 'CMS',
    'skin': 'moono',
    'extraPlugins': 'cmsplugins',
    'toolbar_HTMLField': [
        ['Undo', 'Redo'],
        ['cmsplugins', '-', 'ShowBlocks'],
        ['Format', 'Styles'],
        ['TextColor', 'BGColor', '-', 'PasteText', 'PasteFromWord'],
        ['Maximize', ''],
        '/',
        ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
        ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
        ['HorizontalRule'],
        ['Link', 'Unlink'],
        ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Table'],
        ['Source'],
        ['Link', 'Unlink', 'Anchor'],
    ],
}
boilerplate_name = locals().get('ALDRYN_BOILERPLATE_NAME', 'legacy')
if boilerplate_name == 'bootstrap3':
    CKEDITOR_SETTINGS['stylesSet'] = 'default:/static/js/addons/ckeditor.wysiwyg.js'
    CKEDITOR_SETTINGS['contentsCss'] = ['/static/css/base.css']
else:
    CKEDITOR_SETTINGS['stylesSet'] = 'default:/static/js/modules/ckeditor.wysiwyg.js'
    CKEDITOR_SETTINGS['contentsCss'] = ['/static/css/base.css']


# OPTIONAL REDIS
REDIS_URL = locals().get('REDIS_URL', '')
if REDIS_URL:
    import dj_redis_url
    redis = dj_redis_url.parse(REDIS_URL)
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': str(redis['HOST']) + ':' + str(redis['PORT']),  # '{HOST}:{PORT}'.format(redis),
            'OPTIONS': {
                'DB': 10,
                'PASSWORD': redis['PASSWORD'],
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
                'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 50,
                    'timeout': 20,
                },
                'MAX_CONNECTIONS': 1000,
            },
        },
    }


# django-health-check
for app in [
        'health_check',
        'health_check_db',
        'health_check_cache',
        # 'health_check_storage',
]:
    INSTALLED_APPS.append(app)

if 'CMSCLOUD_SYNC_KEY' not in locals():
    CMSCLOUD_SYNC_KEY = None
if 'LAST_BOILERPLATE_COMMIT' not in locals():
    LAST_BOILERPLATE_COMMIT = None
if 'SYNC_CHANGED_FILES_URL' not in locals():
    SYNC_CHANGED_FILES_URL = None
