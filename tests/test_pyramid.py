import unittest

from nose.plugins import PluginTester
from pyramid import testing
from pyramid.renderers import (
    render,
    render_to_response,
    get_renderer,
)

from templateusage import TemplateUsageReportPlugin

class TemplateUsageReportTestMixin(PluginTester):
    activate = '--with-pyramid-template-usage-report'
    plugins = [TemplateUsageReportPlugin()]

    def makeSuite(self):
        class TestCase(unittest.TestCase):
            def runTest(_self):
                _self.config = testing.setUp()
        return unittest.TestSuite([TestCase()])

class TemplateUsageReportPluginTestCase(TemplateUsageReportTestMixin, unittest.TestCase):
    RENDER_TEMPLATE_NAME = 'pyramid_templates/render.pt'
    GET_RENDERER_TEMPLATE_NAME = 'pyramid_templates/get_renderer.pt'
    RENDER_TO_RESPONSE_TEMPLATE_NAME = 'pyramid_templates/render_to_response.pt'
    args = ('--pyramid-template-match=*.pt',)

    def test_render(self):
        render(self.RENDER_TEMPLATE_NAME, {})
        self.assertIn(self.RENDER_TEMPLATE_NAME, self.plugins[0].used_templates)
        self.assertIn('tests/pyramid_templates/unused.pt', self.plugins[0].unused_templates)

    def test_render_to_response(self):
        render_to_response(self.RENDER_TO_RESPONSE_TEMPLATE_NAME, {})
        self.assertIn(self.RENDER_TO_RESPONSE_TEMPLATE_NAME, self.plugins[0].used_templates)
        self.assertIn('tests/pyramid_templates/unused.pt', self.plugins[0].unused_templates)

    def test_get_renderer(self):
        get_renderer(self.GET_RENDERER_TEMPLATE_NAME)
        self.assertIn(self.GET_RENDERER_TEMPLATE_NAME, self.plugins[0].used_templates)
        self.assertIn('tests/pyramid_templates/unused.pt', self.plugins[0].unused_templates)

    def test_unused(self):
        self.assertIn('tests/pyramid_templates/unused.pt', self.plugins[0].unused_templates)
