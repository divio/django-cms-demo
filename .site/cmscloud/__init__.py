# -*- coding: utf-8 -*-

from django.conf import settings

from cmscloud.sync import sync_changed_files

###############################################################################
# Running the initial sync that should pull all the changes that have been made
# while this container was being deployed (and the old one was still running
# and receiving all the changes).
###############################################################################

if (settings.CMSCLOUD_SYNC_KEY and settings.LAST_BOILERPLATE_COMMIT and
        settings.SYNC_CHANGED_FILES_URL):
    # IMPORTANT this must be run AFTER the settings have been defined because
    # of the raven/sentry exception logging
        sync_changed_files(
            settings.CMSCLOUD_SYNC_KEY, settings.LAST_BOILERPLATE_COMMIT,
            settings.SYNC_CHANGED_FILES_URL, settings.PROJECT_DIR)
