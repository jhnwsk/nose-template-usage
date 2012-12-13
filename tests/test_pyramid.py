import os
import unittest

from nose.plugins import PluginTester

from templateusage import TemplateUsageReportPlugin

class TemplateUsageReportTestMixin(PluginTester):
    activate = '--with-pyramid-template-usage-report'
    plugins = [TemplateUsageReportPlugin()]

    def makeSuite(self):
        try:
            from pyramid import renderers
        except ImportError:
            self.fail("pyramid is not available")
        self.renderers = renderers
        class TestCase(unittest.TestCase):
            def runTest(_self):
                from pyramid import testing
                _self.config = testing.setUp()
        return unittest.TestSuite([TestCase()])

class TemplateUsageReportPluginTestCase(TemplateUsageReportTestMixin, unittest.TestCase):
    RENDER_TEMPLATE_NAME = os.path.abspath('tests/pyramid_templates/render.pt')
    GET_RENDERER_TEMPLATE_NAME = os.path.abspath('tests/pyramid_templates/get_renderer.pt')
    RENDER_TO_RESPONSE_TEMPLATE_NAME = os.path.abspath('tests/pyramid_templates/render_to_response.pt')
    UNUSED_TEMPLATE_NAME = os.path.abspath('tests/pyramid_templates/unused.pt')
    args = ('--pyramid-template-match=*.pt',)

    def test_render(self):
        self.renderers.render(self.RENDER_TEMPLATE_NAME, {})
        self.assertIn(self.RENDER_TEMPLATE_NAME, self.plugins[0].used_templates)
        self.assertIn(self.UNUSED_TEMPLATE_NAME, self.plugins[0].unused_templates)

    def test_render_to_response(self):
        self.renderers.render_to_response(self.RENDER_TO_RESPONSE_TEMPLATE_NAME, {})
        self.assertIn(self.RENDER_TO_RESPONSE_TEMPLATE_NAME, self.plugins[0].used_templates)
        self.assertIn(self.UNUSED_TEMPLATE_NAME, self.plugins[0].unused_templates)

    def test_get_renderer(self):
        self.renderers.get_renderer(self.GET_RENDERER_TEMPLATE_NAME)
        self.assertIn(self.GET_RENDERER_TEMPLATE_NAME, self.plugins[0].used_templates)
        self.assertIn(self.UNUSED_TEMPLATE_NAME, self.plugins[0].unused_templates)

    def test_unused(self):
        self.assertIn(self.UNUSED_TEMPLATE_NAME, self.plugins[0].unused_templates)
