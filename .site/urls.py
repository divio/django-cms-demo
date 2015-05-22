# -*- coding: utf-8 -*-
import re

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from cmscloud.sso import CloudUserClient
from cmscloud.views import trigger_sync_changed_files

admin.autodiscover()


client = CloudUserClient.from_dsn(settings.SSO_DSN)


urlpatterns = patterns(
    '',
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'^robots\.txt$', include('robots.urls')),
    url(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')), 'django.contrib.staticfiles.views.serve', {'insecure': True}),
    url(r'^admin/~cmscloud-api/', include('cmscloud.urls')),
    url(r'^admin/~health-check/', include('health_check.urls')),
    url(r'^login/', include(client.get_urls())),
    url(r'^trigger-sync-changed-files/$', csrf_exempt(trigger_sync_changed_files)),
) + i18n_patterns(
    '',
    # TODO: this should come from a "django-select2" addon... but how to include custom urls?
    url(r'^api/~select2/', include('django_select2.urls')),  # required by: djangocms-link
    url(r'^admin/', include(admin.site.urls)),
    url(r'^captcha/', include('captcha.urls')),  # TODO: this captcha should be an addon
    url(r'^', include('cms.urls')),
)
