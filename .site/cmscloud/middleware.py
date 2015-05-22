# -*- coding: utf-8 -*-
"""
Access Control Middleware
"""
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from cmscloud.sso import ALDRYN_USER_SESSION_KEY


class AccessControlMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            # the user is already logged in
            return None
        if request.path.startswith(('/login/', '/admin/~cmscloud-api/',
                                    '/trigger-sync-changed-files/', '/sitemap.xml')):
            # internal api call, skipping the authentication check
            return None
        if request.session.get(settings.SHARING_VIEW_ONLY_TOKEN_KEY_NAME):
            # the user accessed the website with the sharing token,
            # skipping the authentication check
            return None

        # check if the user is using the "view only sharing url"
        token = request.GET.get(settings.SHARING_VIEW_ONLY_TOKEN_KEY_NAME, None)
        if settings.SHARING_VIEW_ONLY_SECRET_TOKEN == token:
            request.session[settings.SHARING_VIEW_ONLY_TOKEN_KEY_NAME] = token
            return HttpResponseRedirect('/')

        # check if it's a demo website in which case look for the demo access token
        DEMO_ACCESS_TOKEN_KEY_NAME = getattr(settings, 'DEMO_ACCESS_TOKEN_KEY_NAME', None)
        DEMO_ACCESS_SECRET_STRING = getattr(settings, 'DEMO_ACCESS_SECRET_STRING', None)
        if DEMO_ACCESS_TOKEN_KEY_NAME and DEMO_ACCESS_SECRET_STRING:
            demo_access_token = request.GET.get(DEMO_ACCESS_TOKEN_KEY_NAME, None)
            if DEMO_ACCESS_SECRET_STRING == demo_access_token:
                request.session[DEMO_ACCESS_TOKEN_KEY_NAME] = demo_access_token
                try:
                    user = User.objects.get(username='aldryn demo')
                except User.DoesNotExist:
                    user = User(username='aldryn demo')
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
                user.backend = "%s.%s" % (ModelBackend.__module__, ModelBackend.__name__)
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return TemplateResponse(request, 'cmscloud/demo_expired.html')

        return TemplateResponse(request, 'cmscloud/login_screen.html')


# copied from django 1.7a2: https://github.com/django/django/blob/1.7a2/django/contrib/sites/middleware.py
from django.contrib.sites.models import Site


class CurrentSiteMiddleware(object):
    """
    Middleware that sets `site` attribute to request object.
    """

    def process_request(self, request):
        request.site = Site.objects.get_current()


class AldrynUserMiddleware(object):
    """
    Middleware that protects Aldryn Cloud users from hijacking their accounts
    by previously created django users with the same email address or username.
    """

    def process_request(self, request):
        user = request.user
        if ALDRYN_USER_SESSION_KEY in request.session:
            # properly logged in Aldryn Cloud user
            return None
        elif hasattr(user, 'aldryn_cloud_account'):
            # this is an Aldryn Cloud account that wasn't logged in with a sso,
            # deactivating its session.
            user.set_unusable_password()  # sso doesn't require local passwords
            user.save()
            logout(request)
            return HttpResponseRedirect('/')
