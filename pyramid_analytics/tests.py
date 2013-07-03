from datetime import datetime
import logging
from os import path
import unittest

from pyramid.compat import configparser
from pyramid.path import AssetResolver
from pyramid.settings import asbool
from pyramid import testing


class TestConfiguration(unittest.TestCase):
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
                         asbool(settings['analytics.async']))
        self.assertEqual(analytics.default_client.send,
                         asbool(settings['analytics.send']))
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

        settings = {
            'analytics.api_token': 'token',
            'analytics.secret': 'sekret'
        }
        config = testing.setUp(settings=settings)
        config.include('pyramid_analytics')

        # Check config
        self.assertEqual(analytics.default_client.secret,
                         settings['analytics.secret'])


class TestEvents(unittest.TestCase):
    def setUp(self):
        settings = {
            'analytics.api_token': 'token',
            'analytics.secret': 'sekret'
        }
        self.config = testing.setUp(settings=settings)
        self.config.include('pyramid_analytics')
        self.request = testing.DummyRequest()

    def attach_analytics(self):
        from pyramid.events import NewRequest
        # Trigger NewRequest
        self.config.testing_add_subscriber(NewRequest)
        self.request.registry.notify(NewRequest(self.request))

    def test_updated_analytics_user_id(self):
        from pyramid_analytics.events import UpdatedAnalyticsUserId

        self.attach_analytics()

        # Trigger UpdatedAnalyticsUserId
        events = self.config.testing_add_subscriber(UpdatedAnalyticsUserId)
        user_id = "userid"
        self.assertNotEqual(self.request.analytics.user_id, user_id)
        e = UpdatedAnalyticsUserId(self.request, user_id)
        self.request.registry.notify(e)

        self.assertEqual(self.request.analytics.user_id, user_id)
        self.assertEqual([e], events)

    def test_new_request(self):
        from pyramid_analytics.helpers import AnalyticsHelper
        with self.assertRaises(AttributeError):
            self.request.analytics

        self.attach_analytics()
        self.assertIsInstance(self.request.analytics, AnalyticsHelper)

    def test_prerender(self):
        from pyramid.events import BeforeRender

        self.config.testing_add_subscriber(BeforeRender)
        self.attach_analytics()
        e = BeforeRender({'request': self.request})
        self.request.registry.notify(e)

        self.assertItemsEqual(['api_token', 'tracking', 'tracking_json'],
                              e['analytics'].keys())


class TestHelper(unittest.TestCase):
    def setUp(self):
        import analytics
        from pyramid_analytics.helpers import AnalyticsHelper

        self.analytics = analytics
        self.analytics.init('secret', send=False)
        self.helper = AnalyticsHelper('token', None)

    def test_flatten(self):
        from pyramid_analytics.helpers import flatten_dict

        d = {
            'a': 'aa',
            'b': {'bb': 'bbb'},
            'c': {
                'cc': {'ccc': 'cccc'}
            }
        }
        expected_d = {'a': 'aa', 'b__bb': 'bbb', 'c__cc__ccc': 'cccc'}

        self.assertEqual(flatten_dict(d), expected_d)

    # Identify
    def test_identify(self):
        self.helper.user_id = 'userid'
        d = {
            'traits': {'trait1': 'value1'},
            'timestamp': datetime(year=2000, month=1, day=1),
            'context': {'context1': 'value1'},
        }
        self.helper.identify(**d)

    def test_identify_foreign(self):
        d = {
            'user_id': 'myuser',
            'traits': {'trait1': 'value1'},
            'timestamp': datetime(year=2000, month=1, day=1),
            'context': {'context1': 'value1'},
        }
        self.helper.identify_foreign(**d)

    # Track
    def test_track_user_id(self):
        self.helper.user_id = 'userid'
        d = {
            'event': 'myevent',
            'properties': {'property1': 'value1'},
            'timestamp': datetime(year=2000, month=1, day=1),
            'context': {'context1': 'value1'},
        }
        self.helper.track(**d)

    def test_track_no_user_id(self):
        d = {
            'event': 'myevent',
            'properties': {'property1': 'value1'},
            'timestamp': datetime(year=2000, month=1, day=1),
            'context': {'context1': 'value1'},
        }
        self.helper.track(**d)
        expected_event = {
            'event': d['event'],
            'properties': d['properties'],
            'options': d['context']
        }
        self.assertIn(expected_event, self.helper.events)

    def test_track_foreign(self):
        d = {
            'user_id': 'myuser',
            'event': 'myevent',
            'properties': {'property1': 'value1'},
            'timestamp': datetime(year=2000, month=1, day=1),
            'context': {'context1': 'value1'},
        }
        self.helper.track_foreign(**d)
