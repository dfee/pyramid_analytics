import logging

import analytics
from pyramid.compat import json

log = logging.getLogger('analytics')


def flatten_dict(data, lkey=''):
    ret = {}
    for rkey, val in data.items():
        key = lkey + rkey
        if isinstance(val, dict):
            ret.update(flatten_dict(val, key + '__'))
        else:
            ret[key] = val
    return ret


class AnalyticsHelper(object):
    """Analytics helper for tracking
    alias: serialized for JS
    identify: serialized for JS, unless server argument is True
    track: pushed from the server if a user is identified"""

    def __init__(self, api_token, user_id):
        self.api_token = api_token
        self.user_id = str(user_id) if user_id else None
        self.alias = False
        self.events = []

    def identify(self, traits, timestamp=None, context=None):
        """identify a user to segment.io with
        :param traits: data to be associated with the user
        :param timestamp: a datetime.datetime timestamp
        :param context: optional dictionary specified by segment.io
        """
        context = context or {}
        log.info('Identified %s with traits: %s' % (self.user_id, traits))
        analytics.identify(
            user_id=self.user_id,
            traits=traits,
            context=context,
            timestamp=timestamp)

    def identify_foreign(self, user_id, traits, timestamp=None, context=None):
        """identify a user to segment.io with
        :param user_id: the user_id to identify
        :param traits: data to be associated with the user
        :param timestamp: a datetime.datetime timestamp
        :param context: optional dictionary specified by segment.io
        """
        user_id = str(user_id)
        context = context or {}
        log.info('Identified %s with traits: %s' % (user_id, traits))
        analytics.identify(
            user_id=user_id,
            traits=traits,
            context=context,
            timestamp=timestamp)

    def track(self, event, properties=None, timestamp=None, context=None):
        """track an event by js if a user isn't identified
        :param event: the event to track (string)
        :param properties: a dictionary of event details
        :param timestamp: a datetime.datetime timestamp
        :param context: optional dictionary specified by segment.io
        """

        properties = properties or {}
        flattened_p = flatten_dict(properties)
        context = context or {}
        log.info('Tracked %s with properties: %s' % (event, properties))

        if self.user_id:
            analytics.track(
                user_id=self.user_id,
                event=event,
                properties=flattened_p,
                context=context,
                timestamp=timestamp)
            return

        self.events.append({
            'event': event,
            'properties': flattened_p,
            'options': context
        })

    def track_foreign(self, user_id, event, properties=None, timestamp=None,
                      context=None):
        """Track an event for a user who is not attached to this instance's
        request attribute.
        :param user_id: the user_id to track an event for
        :param event: title of the event to track (e.g. 'user_created')
        :param properties: a dictionary of event details
        :param timestamp: a datetime.datetime timestamp
        :param context: optional dictionary specified by segment.io
        """

        user_id = str(user_id)
        properties = properties or {}
        flattened_p = flatten_dict(properties)
        context = context or {}

        log.info('Tracked %s for %s with properties: %s' %
                 (event, user_id, properties))

        analytics.track(
            user_id=user_id,
            event=event,
            properties=flattened_p,
            context=context,
            timestamp=timestamp)

    def serialize(self):
        tracking = {
            'events': self.events,
            'alias': self.user_id if self.alias else None,
            'identify': self.user_id if self.user_id else None
        }
        return {
            'api_token': self.api_token,
            'tracking': tracking,
            'tracking_json': json.dumps(tracking)
        }
