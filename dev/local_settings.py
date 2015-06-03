from settings import *
# override settings as required

INSTALLED_APPS += [
    'aldryn_blueprint',
    'aldryn_segmentation',
    'country_segment',
]

MIDDLEWARE_CLASSES += [
    'country_segment.middleware.ResolveCountryCodeMiddleware'
]

DEBUG = False
