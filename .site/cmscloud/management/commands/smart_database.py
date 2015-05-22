# -*- coding: utf-8 -*-
from copy import deepcopy
import os
from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings
from django.db.transaction import commit_on_success
from django.db.utils import DatabaseError
from django.utils.translation import activate
from optparse import make_option
from south.management.commands.migrate import Command as Migrate
from south.management.commands.syncdb import Command as SyncDB
from django.core.management.commands.createcachetable import Command as CreateCacheTable
from south.models import MigrationHistory
from cmscloud.serialize import Loader


def dummy_http():
    from BaseHTTPServer import BaseHTTPRequestHandler
    import SocketServer
    import os

    content = 'nothing'
    content_lenth = len(content)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-length', content_lenth)
            self.end_headers()
            self.wfile.write(content)


    httpd = SocketServer.TCPServer(('', int(os.environ['PORT'])), Handler)
    print 'serving nothing at port', os.environ['PORT']
    httpd.serve_forever()


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--key', action='store', dest='key'),
        make_option('--idle', action='store_true', dest='idle'),
    ) 
    def handle_noargs(self, **options):
        key = options.pop('key', '')
        idle = options.pop('idle', False)
        syncdb_opts = deepcopy(options)
        syncdb_opts['migrate_all'] = False
        syncdb_opts['interactive'] = False
        syncdb_opts['migrate'] = False
        syncdb_opts['database'] = 'default'
        migrate_opts = deepcopy(options)
        migrate_opts['fake'] = False
        migrate_opts['interactive'] = False

        try:
            cachetable = CreateCacheTable()
            cachetable.stdout = self.stdout
            cachetable.stderr = self.stderr
            cachetable.handle('django_dbcache', database='default')
            self.stdout.write('created cache table "django_dbcache"')
        except CommandError:
            self.stdout.write('not created cache table "django_dbcache". already exists.')

        self.stdout.write("Detecting database status\n")
        try:
            with commit_on_success():
                MigrationHistory.objects.count()
        except DatabaseError:
            self.stdout.write("No database yet, but NOT running full syncdb anyway (because that causes problems with django-cms 3 cms plugin table renames).\n")
            if False:
                self.stdout.write("No database yet, running full syncdb\n")
                syncdb_opts['migrate_all'] = True
                migrate_opts['fake'] = True
        syncdb = SyncDB()
        syncdb.stdout = self.stdout
        syncdb.stderr = self.stderr
        syncdb.handle_noargs(**syncdb_opts)
        migrate = Migrate()
        migrate.stdout = self.stdout
        migrate.stderr = self.stderr
        migrate.handle(**migrate_opts)
        datayaml = os.path.join(settings.PROJECT_DIR, 'data.yaml')
        if os.path.exists(datayaml):
            self.stdout.write("Found data.yaml, trying to load.\n")
            activate(settings.CMS_LANGUAGES[0][0])
            os.chdir(settings.PROJECT_DIR)
            loader = Loader()
            loader.load(datayaml)
        else:
            self.stdout.write("data.yaml not found, not loading any data.\n")
        if idle:
            self.stdout.write("running dummy http server for unknown reasons.\n")
            dummy_http()

