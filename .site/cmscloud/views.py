# -*- coding: utf-8 -*-
from collections import defaultdict
import inspect
import json
import os

from cms.app_base import CMSApp
from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.utils.django_load import get_module
from django.conf import settings
from django.forms.forms import NON_FIELD_ERRORS
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404)
from django.template.loader import render_to_string
from django.views.generic import View
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from cmscloud.forms import AddForm, DeleteForm
from cmscloud.sync import sync_changed_files

LIVERELOAD_ACTIVE_SESSION_KEY = '_livereload_active'
LIVERELOAD_ACTIVE_DEFAULT = True


def safe_get_module(*args):
    try:
        return get_module(*args)
    except ImportError:
        return None


def check_uninstall_ok(request):
    apps = request.GET.get('apps', '').split(',')
    if apps == ['']:
        return HttpResponseBadRequest("no apps provided")
    plugin_names = []
    apphooks = []
    menus = []
    for app in apps:
        module = safe_get_module(app, "cms_plugins", False, False)
        if module:
            for cls_name in dir(module):
                print cls_name
                cls = getattr(module, cls_name)
                if inspect.isclass(cls) and issubclass(cls, CMSPluginBase):
                    plugin_names.append(cls.__name__)
        module = safe_get_module(app, "cms_app", False, False)
        if module:
            for cls_name in dir(module):
                cls = getattr(module, cls_name)
                if inspect.isclass(cls) and issubclass(cls, CMSApp) and cls.__name__ not in apphooks:
                    apphooks.append(cls.__name__)
        module = safe_get_module(app, "menu", False, False)
        if module:
            for cls_name in dir(module):
                cls = getattr(module, cls_name)
                if hasattr(cls, 'cms_enabled') and cls.cms_enabled and cls.__name__ not in menus:
                    menus.append(cls.__name__)
    plugin_count = {}
    for plugin_type in plugin_names:
        count = CMSPlugin.objects.filter(plugin_type=plugin_type).count()
        if count:
            plugin_count[plugin_type] = count
    apphook_count = []
    for hook in apphooks:
        exists = Page.objects.filter(application_urls=hook).exists()
        if exists:
            apphook_count.append(hook)
    menu_count = []
    for menu in menus:
        exists = Page.objects.filter(navigation_extenders=menu).exists()
        if exists:
            menu_count.append(menu)
    if plugin_count or apphook_count or menu_count:
        result = {'plugins': plugin_count, 'apphooks': apphook_count, 'menus': menu_count}
    else:
        result = 'ok'
    return HttpResponse(json.dumps(result), content_type="application/json")


def check_plugins(request):
    plugins = request.GET.get('plugins', '').split(',')
    count = CMSPlugin.objects.filter(plugin_type__in=plugins).count()
    return HttpResponse(str(count))


def check_apphooks(request):
    apphooks = request.GET.get('apphooks', '').split(',')
    count = Page.objects.filter(application_urls__in=apphooks).count()
    return HttpResponse(str(count))


def errors_to_json(form):
    output = defaultdict(list)
    for field, errors in form.errors.items():
        for error in errors:
            output[form[field].label if field != NON_FIELD_ERRORS else NON_FIELD_ERRORS].append(error)
    return json.dumps(output)


class Add(View):
    form = AddForm

    def post(self, request):
        if not getattr(settings, 'CMSCLOUD_SYNC_KEY'):
            raise Http404()
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            self.save(form.clean())
            return HttpResponse('', status=204)
        else:
            return HttpResponseBadRequest(errors_to_json(form), content_type='application/json')

    def save(self, data):
        full_path = os.path.join(settings.PROJECT_DIR, data['path'])
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(full_path, 'w') as fobj:
            for chunk in data['content'].chunks():
                fobj.write(chunk)


class Delete(Add):
    form = DeleteForm

    def save(self, data):
        full_path = os.path.join(settings.PROJECT_DIR, data['path'])
        if os.path.exists(full_path):
            os.remove(full_path)


def toggle_livereload(request):
    livereload_active = request.session.get(
        LIVERELOAD_ACTIVE_SESSION_KEY, LIVERELOAD_ACTIVE_DEFAULT)
    request.session[LIVERELOAD_ACTIVE_SESSION_KEY] = not livereload_active
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def get_livereload_iframe_content(request):
    CONTENT = ''
    if request.user.is_authenticated():
        livereload_active = request.session.get(
            LIVERELOAD_ACTIVE_SESSION_KEY, LIVERELOAD_ACTIVE_DEFAULT)
        livereload_credential_url = getattr(
            settings, 'LIVERELOAD_CREDENTIAL_URL', None)
        if livereload_active and livereload_credential_url:
            CONTENT = render_to_string(
                'cmscloud/livereload_iframe_content.html',
                {
                    'CMSCLOUD_STATIC_URL': settings.CMSCLOUD_STATIC_URL,
                    'LIVE_RELOAD_CREDENTIAL_URL': livereload_credential_url,
                    'CURRENTLY_LOGGED_IN_USER_EMAIL': request.user.email
                })
    return HttpResponse(CONTENT)


def trigger_sync_changed_files(request):
    sync_key = settings.CMSCLOUD_SYNC_KEY
    if (sync_key and settings.LAST_BOILERPLATE_COMMIT and
            settings.SYNC_CHANGED_FILES_URL):
        # trigger the sync only on the stage websites
        if 'signature' in request.POST:
            # make sure that only trusted
            signature = request.POST['signature']
            signer = URLSafeTimedSerializer(sync_key)
            try:
                signer.loads(
                    signature,
                    max_age=settings.SYNC_CHANGED_FILES_SIGNATURE_MAX_AGE)
            except (SignatureExpired, BadSignature) as e:
                return HttpResponseBadRequest(e.message)
            sync_changed_files(
                sync_key, settings.LAST_BOILERPLATE_COMMIT,
                settings.SYNC_CHANGED_FILES_URL, settings.PROJECT_DIR)
    return HttpResponse('ok')
