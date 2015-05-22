# -*- coding: utf-8 -*-
import hashlib
import hmac
from django import forms
from django.conf import settings
from django.utils.crypto import constant_time_compare


class DeleteForm(forms.Form):
    signature = forms.CharField(required=True)
    path = forms.CharField(required=True)

    def clean_path(self):
        path = self.cleaned_data.get('path', '')
        if path == 'cms_templates.json':
            return path
        elif not path.startswith(('static/', 'templates/')):
            raise forms.ValidationError('Invalid path: "%s"' % path)
        return path

    def clean(self):
        data = super(DeleteForm, self).clean()
        path = data['path']
        signature = data['signature']
        generated_signature = hmac.new(str(settings.CMSCLOUD_SYNC_KEY), path, hashlib.sha1).hexdigest()
        if not constant_time_compare(signature, generated_signature):
            raise forms.ValidationError("Invalid signature")
        return data


class AddForm(DeleteForm):
    content = forms.FileField(required=True, allow_empty_file=True)

    def clean(self):
        data = super(DeleteForm, self).clean()
        path = data.get('path')
        uploaded_file = data.get('content')
        signature = data.get('signature')
        if path and uploaded_file and signature:  # otherwise there were some errors
            signature_hmac = hmac.new(str(settings.CMSCLOUD_SYNC_KEY), path, hashlib.sha1)
            for chunk in uploaded_file.chunks():
                signature_hmac.update(chunk)
            generated_signature = signature_hmac.hexdigest()
            if not constant_time_compare(signature, generated_signature):
                raise forms.ValidationError("Invalid signature")
        return data
