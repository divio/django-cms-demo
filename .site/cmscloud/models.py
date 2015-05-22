# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from cmscloud.template_api import registry


###########################################
# Live html/css/js reload on stage server #
###########################################
def live_reload(request=None):
    live_reload_credential_url = getattr(
        settings, 'LIVERELOAD_CREDENTIAL_URL', None)
    if not live_reload_credential_url:
        return ''

    return '<iframe src="%s" style="display: none;"></iframe>' % reverse('livereload-iframe-content')

registry.add_to_tail(live_reload)


#########################
# apphook server reload #
#########################
import cms.signals
import requests


def trigger_server_restart(**kwargs):
    restarter_url = getattr(settings, 'RESTARTER_URL', None)
    if restarter_url:
        requests.post(restarter_url, data={
                      'info': getattr(settings, 'RESTARTER_PAYLOAD', None)})

cms.signals.urls_need_reloading.connect(
    trigger_server_restart, dispatch_uid='aldryn-cms-cloud-apphook')


#######################
# apply monkeypatches #
#######################
from .monkeypatches import hide_secrets_in_debug_mode
hide_secrets_in_debug_mode.patch()


####################################
# Login service user with cloud_id #
####################################

class AldrynCloudUserManager(models.Manager):
    def get_query_set(self):
        return super(AldrynCloudUserManager, self).get_query_set().select_related('user')


class AldrynCloudUser(models.Model):
    cloud_id = models.PositiveIntegerField(unique=True)
    user = models.OneToOneField(User, unique=True, related_name='aldryn_cloud_account')

    objects = AldrynCloudUserManager()
