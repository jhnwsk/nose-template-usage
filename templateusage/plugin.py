import json
import os
import string
import sys
import mock
import fnmatch

from nose.plugins.base import Plugin

LINE_LENGTH = 70

def heading(stream, value):
    print >> stream, '=' * LINE_LENGTH
    print >> stream, value
    print >> stream, '-' * LINE_LENGTH


def bulleted(stream, values):
    for value in values:
        print >> stream, ' * ', value


def files(directory, matches = ['*']):
    """
    Returns a set of paths of all files located within the provided directory.
    """
    paths = set()
    for dirpath, dirnames, filenames in os.walk(directory):
        filtered = []
        for m in matches: filtered.extend(fnmatch.filter(filenames, m))
        for filename in filtered:
            path = os.path.join(dirpath, filename)
            paths.add(os.path.relpath(path, directory))
    return paths


class TemplateUsageReportPlugin(Plugin):
    enabled = False
    django_enabled = False

    pyramid_enabled = False
    pyramid_template_match = []

    score = sys.maxint

    django = 'django-template-usage-report'
    pyramid = 'pyramid-template-usage-report'

    def options(self, parser, env):
        parser.add_option('--with-%s' % self.django, dest='django_enabled', default=False,
            action='store_true', help='Enable django template usage reporting.')

        parser.add_option('--with-%s' % self.pyramid, dest='pyramid_enabled', default=False,
            action='store_true', help='Enable pyramid template usage reporting.')

        parser.add_option("--ignore-template-prefix", dest='ignore_prefixes',
            action='append', help='Add a template directory to the ignore list.',
            default=[])

        parser.add_option("--pyramid-template-match", dest='pyramid_template_match',
            action='append', help='Add regexp pattern matching pyramid template files.',
            default=[])

        parser.add_option('--template-usage-report-file', dest='outfile',
            help='Write JSON template usage report to file.')

    def configure(self, options, conf):
        self.django_enabled = options.django_enabled

        self.pyramid_template_match = options.pyramid_template_match
        self.pyramid_enabled = options.pyramid_enabled

        self.enabled = self.django_enabled or self.pyramid_enabled
        if not self.enabled:
            return

        ignore_prefixes = options.ignore_prefixes
        # Allow for multiple values in a single argument, e.g. from `setup.cfg`.
        if len(ignore_prefixes) == 1:
            ignore_prefixes = map(string.strip, ignore_prefixes[0].split('\n'))

        self.ignore_prefixes = ignore_prefixes
        self.outfile = options.outfile

    def begin(self):
        self.used_templates = set()

        if self.django_enabled:
            from django.template.loader import find_template
            def register_django_template_usage(name, *args, **kwargs):
                result = find_template(name, *args, **kwargs)
                self.used_templates.add(name)
                return result

            # why can't you autospec this?
            # does find_template import other stuff?
            self.django_patch = mock.patch('django.template.loader.find_template',
                                    side_effect=register_django_template_usage)
            self.django_patch.start()

        if self.pyramid_enabled:
            from pyramid.renderers import RendererHelper
            def register_pyramid_template_usage(name, *args, **kwargs):
                result = RendererHelper(name, *args, **kwargs)
                self.used_templates.add(name)
                return result

            self.pyramid_patch = mock.patch('pyramid.renderers.RendererHelper',
                                            side_effect=register_pyramid_template_usage)
            self.pyramid_patch.start()

    def report(self, stream):
        heading(stream, 'Used Templates (%s)' % len(self.used_templates))
        bulleted(stream, sorted(self.used_templates))
        available_templates = set()

        if self.django_enabled:
            from django.conf import settings
            from django.template.loader import template_source_loaders
            from django.template.loaders.filesystem import Loader as FileSystemLoader
            from django.template.loaders.app_directories import Loader as AppDirectoryLoader

            def filter_ignored(paths):
                for path in paths:
                    for prefix in self.ignore_prefixes:
                        if os.path.commonprefix((prefix, path)) == prefix:
                            break
                    else:
                        yield path

            for loader in template_source_loaders:
                # XXX: This should only execute once per class since you can't
                # actually instantiate the loaders multiple times.
                if isinstance(loader, FileSystemLoader):
                    for directory in settings.TEMPLATE_DIRS:
                        available_templates.update(filter_ignored(files(directory)))

                elif isinstance(loader, AppDirectoryLoader):
                    from django.template.loaders.app_directories import app_template_dirs
                    for directory in app_template_dirs:
                        available_templates.update(filter_ignored(files(directory)))

        if self.pyramid_enabled:
            available_templates.update(files('.', self.pyramid_template_match))

        self.unused_templates = available_templates - self.used_templates
        heading(stream, 'Unused Templates (%s)' % len(self.unused_templates))
        bulleted(stream, sorted(self.unused_templates))

        if self.outfile:
            with open(self.outfile, 'w') as out:
                json.dump({
                    'used': list(self.used_templates),
                    'unused': list(self.unused_templates),
                }, out)
