# -*- coding: utf-8 -*-
from collections import defaultdict
import hashlib
import shutil
import os
import yaml
import glob


# YAML STUFF


class Include(object):
    def __init__(self, path):
        self.path = path

class ListInclude(Include): pass

class File(Include): pass

class LiteralInclude(Include): pass

class Model(object):
    def __init__(self, app_label, model_name):
        self.app_label = app_label
        self.model_name = model_name

def include_constructor(loader, node):
    value = loader.construct_scalar(node).lstrip('/')
    with open(value) as fobj:
        return yaml.load(fobj)

def include_representer(dumper, data):
    return dumper.represent_scalar(u'!include', u'%s' % data.path)

def list_include_constructor(loader, node):
    value = loader.construct_scalar(node).lstrip('/')
    data = []
    for fname in glob.glob(value):
        with open(fname) as fobj:
            data += yaml.load(fobj)
    return data

def list_include_representer(dumper, data):
    return dumper.represent_scalar(u'!list-include', data.path)

def file_constructor(loader, node):
    from django.core.files import File
    value = loader.construct_scalar(node).lstrip('/')
    return File(open(value))

def file_representer(dumper, data):
    return dumper.represent_scalar(u'!file', data.path)

def literal_include_constructor(loader, node):
    with file_constructor(loader, node) as fobj:
        return fobj.read()

def literal_include_representer(dumper, data):
    return dumper.represent_scalar(u'!literal-include', data.path)


def model_constructor(loader, node):
    from django.db.models.loading import get_model
    app_label, model_name = loader.construct_scalar(node).split('.')
    return get_model(app_label, model_name)

def model_representer(dumper, data):
    return dumper.represent_scalar(u'!model', '%s.%s' % (data.app_label, data.model_name))

yaml.add_constructor(u'!include', include_constructor)
yaml.add_constructor(u'!include-list', list_include_constructor)
yaml.add_constructor(u'!literal-include', literal_include_constructor)
yaml.add_constructor(u'!file', file_constructor)
yaml.add_representer(Include, include_representer)
yaml.add_representer(ListInclude, list_include_representer)
yaml.add_representer(File, file_representer)
yaml.add_representer(LiteralInclude, literal_include_representer)
yaml.add_constructor(u'!model', model_constructor)
yaml.add_representer(Model, model_representer)

# DUMP


class Dumper(object):
    def __init__(self, datadir, language, follow=None):
        self.datadir = datadir
        if os.path.exists(self.datadir):
            shutil.rmtree(self.datadir)
        os.mkdir(self.datadir)
        self.file_count = 0
        self.language = language
        self.follow = defaultdict(list)
        if follow:
            for key, value in (thing.split('.', 1) for thing in follow):
                self.follow[key].append(value)
        from cms import models
        self.cms_models = models
        self.file_cache = {}

    def dump(self, filename):
        data = self.get_pages()
        with open(filename, 'w') as fobj:
            yaml.dump(data, fobj)

    def get_pages(self):
        data = []
        for page in self.cms_models.Page.objects.root():
            data.append(self.serialize_page(page))
        return data

    def serialize_page(self, page):
        return {
            'path': page.get_absolute_url(),
            'name': page.get_title(),
            'template': page.template,
            'placeholders': [self.serialize_placeholder(page, ph) for ph in page.placeholders.all()],
            'children': [self.serialize_page(child) for child in page.get_children()],
            }

    def serialize_placeholder(self, page, placeholder):
        plugins = self.dump_plugins(page, placeholder)
        return {
            'name': placeholder.slot,
            'plugins': Include(plugins)
        }

    def dump_plugins(self, page, placeholder):
        filename = os.path.join(self.datadir, '%s_%s.yaml' % (placeholder.slot, page.pk))
        data = [self.serialize_plugin(plugin) for plugin in placeholder.cmsplugin_set.filter(language=self.language, parent__isnull=True).order_by('position')]
        with open(filename, 'w') as fobj:
            yaml.dump(data, fobj)
        return filename

    def serialize_plugin(self, plugin):
        from django.forms.models import model_to_dict
        instance = plugin.get_plugin_instance()[0]
        raw_data = model_to_dict(instance)
        raw_data.pop('cmsplugin_ptr', None)
        del raw_data['id']
        raw_data['plugin_type'] = plugin.plugin_type
        raw_data['-relations'] = []
        raw_data['-children'] = []
        self.post_process_files(raw_data)
        self.post_process_relations(instance, plugin, raw_data)
        self.post_process_children(instance, plugin, raw_data)
        return raw_data

    def post_process_files(self, raw_data):
        from django.db.models.fields.files import FieldFile, ImageFieldFile
        for key, value in raw_data.items():
            if isinstance(value, (FieldFile, ImageFieldFile)):
                if value:
                    data = ''
                    for chunk in value.chunks():
                        data += chunk
                        #de-dup
                    checksum = hashlib.md5(data).hexdigest()
                    if checksum not in self.file_cache:
                        filename = os.path.join(self.datadir, '_file_%s' % self.file_count)
                        self.file_count += 1
                        with open(filename, 'wb') as target:
                            target.write(data)
                        self.file_cache[checksum] = filename
                    raw_data[key] = File(self.file_cache[checksum])
                else:
                    raw_data[key] = None

    def post_process_relations(self, instance, plugin, raw_data):
        for field in self.follow['%s:%s' % (instance._meta.app_label, instance._meta.module_name)]:
            objects = getattr(instance, field).all()
            raw_data['-relations'] += [self.serialize_plugin_relation(instance, obj) for obj in objects]

    def serialize_plugin_relation(self, plugin, obj):
        from django.forms.models import model_to_dict
        from django.db.models.fields.related import ForeignKey
        data = model_to_dict(obj, fields=obj._meta.get_all_field_names())
        for field_name in obj._meta.get_all_field_names():
            field = obj._meta.get_field_by_name(field_name)[0]
            if isinstance(field, ForeignKey):
                if getattr(obj, field_name) == plugin:
                    del data[field_name]
                    data['-field'] = field_name
            elif field_name not in data:
                data[field_name] = field.value_from_object(obj)
        del data['id']
        self.post_process_files(data)
        data['-model'] = Model(obj._meta.app_label, obj.__class__.__name__)
        return data

    def post_process_children(self, instance, plugin, raw_data):
        pass

# LOAD

class Loader(object):
    def syncdb(self):
        from django.core.management import call_command
        from django.conf import settings
        call_command('syncdb', interactive=False)
        if 'south' in settings.INSTALLED_APPS:
            call_command('migrate', interactive=False)

    def load(self, filename):
        self.syncdb()
        from cms.models import Page
        if Page.objects.exists():
            print "Non-empty database, aborting"
            return
        with open(filename) as fobj:
            data = yaml.load(fobj)
            for page in data:
                self.load_page(page)

    def load_page(self, data, parent=None):
        from cms.api import create_page
        from cms.models import Page
        from django.utils.translation import get_language
        if parent:
            parent = Page.objects.get(pk=parent.pk)
        page = create_page(data['name'], data['template'], 'en', parent=parent,
            in_navigation=True, published=True)
        for placeholder in data['placeholders']:
            self.load_placeholder(placeholder, page)
        for child in data['children']:
            self.load_page(child, page)

    def load_placeholder(self, data, page):
        placeholder = page.placeholders.get(slot=data['name'])
        for plugin in data['plugins']:
            self.load_plugin(plugin, placeholder)

    def load_plugin(self, data, placeholder, parent=None):
        from cms.api import add_plugin
        from django.utils.translation import get_language
        plugin_type = data.pop('plugin_type')
        relations = data.pop('-relations')
        children = data.pop('-children')
        plugin = add_plugin(placeholder, plugin_type, 'en', target=parent, **data)
        for child in children:
            self.load_plugin(child, placeholder, plugin)
        for relation in relations:
            self.load_relation(relation, plugin)

    def load_relation(self, data, plugin):
        model = data.pop('-model')
        plugin_field = data.pop('-field')
        data[plugin_field] = plugin
        model.objects.create(**data)


def dump(args):
    Dumper(args.datadir, args.language, args.follow).dump(args.filename)

def load(args):
    Loader().load(args.filename)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--settings', default='settings')
    parser.add_argument('--language', default='en')
    subparsers = parser.add_subparsers()
    dump_parser = subparsers.add_parser('dump')
    dump_parser.add_argument('datadir')
    dump_parser.add_argument('--follow', action='append', default=[])
    dump_parser.set_defaults(func=dump)
    load_parser = subparsers.add_parser('load')
    load_parser.set_defaults(func=load)
    args = parser.parse_args()
    os.environ['DJANGO_SETTINGS_MODULE'] = args.settings
    from django.utils.translation import activate
    activate(args.language)
    args.func(args)
