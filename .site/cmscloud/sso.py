# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from simple_sso.sso_client.client import Client, AuthenticateView

from cmscloud.models import AldrynCloudUser

ALDRYN_USER_SESSION_KEY = '_aldryn_user'


class QuickerExpirationAuthenticateView(AuthenticateView):
    def get(self, request):
        response = super(QuickerExpirationAuthenticateView, self).get(request)
        request.session[ALDRYN_USER_SESSION_KEY] = True
        request.session.set_expiry(settings.CLOUD_USER_SESSION_EXPIRATION)
        request.session.save()
        return response


class CloudUserClient(Client):
    authenticate_view = QuickerExpirationAuthenticateView
    user_extra_data = ['cloud_id']

    def _get_free_username(self, original_username):
        username = original_username
        i = 1
        while User.objects.filter(username=username).exists():
            username = u'%s - %s' % (original_username, i)
            i += 1
        return username

    def build_user(self, user_data):
        extra_data = user_data.pop('extra_data')
        cloud_id = extra_data['cloud_id']
        try:
            account = AldrynCloudUser.objects.get(cloud_id=cloud_id)
        except AldrynCloudUser.DoesNotExist:
            username = user_data.pop('username')
            email = user_data.pop('email')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username, email=email)
                user.save()
            else:
                # User with this username already exists. Checking if the emails
                # matches, otherwise creating a new user.
                if user.email != email:
                    free_username = self._get_free_username(username)
                    user = User(username=free_username, email=email)
            account = AldrynCloudUser(cloud_id=cloud_id, user=user)
            account.save()
        else:
            user = account.user
        for key, value in user_data.items():
            setattr(user, key, value)
        user.set_unusable_password()
        user.save()
        return user
