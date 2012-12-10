import unittest

from nose.plugins import PluginTester
from pyramid.renderers import (
    render,
)

from templateusage import TemplateUsageReportPlugin

class TemplateUsageReportTestMixin(PluginTester):
    TEMPLATE_NAME = 'example.pt'

    activate = '--with-pyramid-template-usage-report'
    plugins = [TemplateUsageReportPlugin()]

    def makeSuite(self):
        class TestCase(unittest.TestCase):
            def runTest(_self):

                import nose.tools
                nose.tools.set_trace()
                render(self.TEMPLATE_NAME, {})
        return unittest.TestSuite([TestCase()])

class TemplateUsageReportPluginTestCase(TemplateUsageReportTestMixin, unittest.TestCase):
    args = ('--pyramid-template-match=*.pt',)

    def test_basic(self):
        self.assertIn(self.TEMPLATE_NAME, self.plugins[0].used_templates)

    def test_included(self):
        self.assertIn('included.pt', self.plugins[0].used_templates)

    def test_unused(self):
        self.assertIn('tests/pyramid_templates/unused.pt', self.plugins[0].unused_templates)

