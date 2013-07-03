import logging

from pyramid.security import authenticated_userid

from .helpers import AnalyticsHelper

log = logging.getLogger('analytics')


class UpdatedAnalyticsUserId(object):
    def __init__(self, request, user_id, alias=False):
        self.request = request
        self.user_id = str(user_id)
        self.alias = alias


def update_analytics_user_id(event):
    analytics = event.request.analytics
    analytics.user_id = event.user_id
    log.info("Analytics associated with %s" % event.user_id)


def add_analytics_to_request(event):
    request = event.request
    user_id = authenticated_userid(request)
    api_token = request.registry.settings['analytics.api_token']
    request.analytics = AnalyticsHelper(api_token, user_id)


def add_analytics_prerender(event):
    request = event['request']
    event['analytics'] = request.analytics.serialize()
