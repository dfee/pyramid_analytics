from datetime import timedelta
import logging

import analytics


def string_to_bool(string):
    """ Returns ``True`` if string is "True", otherwise, returns ``False`` """
    return string == 'True'


def includeme(config):
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

    settings = config.registry.settings

    # Logging
    analytics_log = logging.getLogger('analytics')
    log_level = analytics_log.level

    # Flush configuration
    flush_at = int(settings.get('analytics.flush_at', '20').strip())
    flush_seconds = int(settings.get('analytics.flush_after', '10').strip())
    flush_after = timedelta(seconds=flush_seconds)

    # Other environment details
    secret = settings.get('analytics.secret').strip()
    async = string_to_bool(settings.get('analytics.async', 'True').strip())
    send = string_to_bool(settings.get('analytics.send', 'True').strip())
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
