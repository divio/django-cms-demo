# -*- coding: utf-8 -*-
"""
hides some more secret variables in the debug error view of django
"""


def patch():
    import re
    from django.views import debug
    signatures = 'API|TOKEN|KEY|SECRET|PASS|PROFANITIES_LIST|SIGNATURE'\
                 '|DSN|RESTARTER_PAYLOAD|REDIS_URL|EMAIL_URL'
    debug.HIDDEN_SETTINGS = re.compile(signatures)