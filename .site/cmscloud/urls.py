# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from cmscloud.views import Add, Delete, get_livereload_iframe_content, toggle_livereload

urlpatterns = patterns(
    '',
    url(r'^check-uninstall/$', 'cmscloud.views.check_uninstall_ok'),
    url(r'^add-file/$', csrf_exempt(Add.as_view())),
    url(r'^delete-file/$', csrf_exempt(Delete.as_view())),
    url(r'^livereload/$', get_livereload_iframe_content,
        name='livereload-iframe-content'),
    url(r'^toggle-livereload/$', toggle_livereload,
        name='toggle-livereload'),
)
