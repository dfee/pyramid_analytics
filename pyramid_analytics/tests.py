import logging
from os import path
import unittest

from pyramid.compat import configparser
from pyramid.path import AssetResolver
from pyramid import testing

from pyramid_analytics import string_to_bool


class TestHelper(unittest.TestCase):
    def test_true(self):
        self.assertTrue(string_to_bool('True'))

    def test_false(self):
        self.assertFalse(string_to_bool('False'))
        self.assertFalse(string_to_bool(None))
        self.assertFalse(string_to_bool('anything_else'))


class TestPyramidIntegration(unittest.TestCase):
    def get_parser(self, ini_filename='test.ini'):
        medici = AssetResolver('pyramid_analytics')
        app_path = medici.resolve('').abspath()
        project_path = path.split(app_path)[0]
        ini_path = path.join(project_path, 'pyramid_analytics', ini_filename)
        parser = configparser.SafeConfigParser()
        parser.read(ini_path)
        return parser

    def setup_logging(self, parser):
        logger_settings = dict(parser.items('logger_analytics'))

        analytics_logger = logging.getLogger(logger_settings['qualname'])
        analytics_logger.setLevel(logger_settings['level'])
        analytics_logger.propagate = int(logger_settings['propagate'])

    def test_analytics_full_config(self):
        import analytics

        parser = self.get_parser()
        self.setup_logging(parser)

        settings = dict(parser.items('app:testapp'))

        config = testing.setUp(settings=settings)
        config.include('pyramid_analytics')

        # Check config
        self.assertEqual(analytics.default_client.secret,
                         settings['analytics.secret'])
        self.assertEqual(analytics.default_client.flush_at,
                         int(settings['analytics.flush_at']))
        self.assertEqual(analytics.default_client.flush_after.seconds,
                         int(settings['analytics.flush_after']))
        self.assertEqual(analytics.default_client.async,
                         string_to_bool(settings['analytics.async']))
        self.assertEqual(analytics.default_client.send,
                         string_to_bool(settings['analytics.send']))
        self.assertEqual(analytics.default_client.max_queue_size,
                         int(settings['analytics.max_queue_size']))

        # Check logging
        log_config = dict(parser.items('logger_analytics'))
        analytics_logger = logging.getLogger(log_config['qualname'])
        self.assertEqual(analytics_logger.propagate,
                         int(log_config['propagate']))
        self.assertEqual(analytics_logger.level,
                         getattr(logging, log_config['level']))

    def test_analytics_minimal_config(self):
        import analytics

        settings = {'analytics.secret': 'sekret'}

        config = testing.setUp(settings=settings)
        config.include('pyramid_analytics')

        # Check config
        self.assertEqual(analytics.default_client.secret,
                         settings['analytics.secret'])

