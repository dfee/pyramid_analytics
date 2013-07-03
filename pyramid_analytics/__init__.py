from datetime import timedelta
import logging

import analytics
from pyramid.events import BeforeRender, NewRequest
from pyramid.settings import asbool

from .events import (
    add_analytics_prerender,
    add_analytics_to_request,
    update_analytics_user_id,
    UpdatedAnalyticsUserId)

log = logging.getLogger('analytics')


def initialize_analytics(settings):
    """ Provide useful configuration to a Pyramid ``Configurator`` instance.

    Currently, this hook will set up and register Segment.io's analytics.
    The following configurations are required in your configuration file:
        ``analytics.secret``
        ``analytics.flush_at``
        ``analytics.flush_after``
        ``analytics.async``
        ``analytics.send``
        ``analytics.max_queue_size``

    Other configuration data should be copied from your Segment.io panel.
    More at http://segment.io.
    """

    # Logging
    analytics_log = logging.getLogger('analytics')
    log_level = analytics_log.level

    # Flush configuration
    flush_at = int(settings.get('analytics.flush_at', '20').strip())
    flush_seconds = int(settings.get('analytics.flush_after', '10').strip())
    flush_after = timedelta(seconds=flush_seconds)

    # Other environment details
    secret = settings.get('analytics.secret').strip()
    async = asbool(settings.get('analytics.async', 'True').strip())
    send = asbool(settings.get('analytics.send', 'True').strip())
    max_queue_size = int(settings.get(
        'analytics.max_queue_size', '10').strip())

    analytics.init(
        secret,
        log_level=log_level,
        flush_at=flush_at,
        flush_after=flush_after,
        async=async,
        send=send,
        max_queue_size=max_queue_size)


def includeme(config):
    settings = config.registry.settings
    initialize_analytics(settings)
    config.add_subscriber(add_analytics_prerender, BeforeRender)
    config.add_subscriber(add_analytics_to_request, NewRequest)
    config.add_subscriber(update_analytics_user_id, UpdatedAnalyticsUserId)
