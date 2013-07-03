pyramid_analytics
=================

Segment.io initializer for the Pyramid Web Framework. 100% Nose Test Covered.

Configuration
-------------
- To use pyramid_analytics, you should include the following directive in your
  configuration file::

    pyramid.includes =
        pyramid_analytics

- The following configuration options are available. Note, 
  ``analytics.api_token`` and ``analytics.secret`` are required.::

    analytics.api_token = mytoken
    analytics.async = True
    analytics.flush_after = 10
    analytics.flush_at = 20
    analytics.max_queue_size = 100000
    analytics.secret = mysekret
    analytics.send = True
  
- ``flush_after`` specifies after how much time (in seconds) of no flushing 
  that the server will flush. Used in conjunction with the flush_at size 
  policy.

- To manage the ``log_level`` and ``log`` options specified by Segment.io's
  analytics-python, you should set the following configuration in your .ini
  file::

    [logger_analytics]
    level = WARN
    handlers = console  # The config needs to include this handler
    qualname = analytics
    propagate = 0  # This "disables" logging
    formatter = generic  # The config needs to include this formatter  

  Additionally, you'll want to register this logger:

- Under the hood, analytics-python turns logging "off" by setting the logging
  level to ``CRITICAL``. Setting ``propagate = 0`` is perhaps a more elegant
  solution.
  
- All other options are detailed at `Segment.io's Python Documentation 
  <https://segment.io/libraries/python>`_.


Pyramid Integration
-------------------
- This library attaches an attribute, ``analytics``, to the request object.
  pyramid_analytics checks for an ``authenticated_userid`` with the Pyramid
  api, and will identify or track data for the authenticated user.

- To update the userid that this ``analytics`` package makes calls on behalf
  of, you should send a new ``UpdatedAnalyticsUserId`` event. Example::

    from pyramid_analytics.events import UpdatedAnalyticsUserId

    # ...
    # User logged in
    event = UpdatedAnalyticsUserId(request, userid, alias=False)
    request.registry.notify(event)

  This event will update the analytic. If a user registers for your service,
  you should set ``alias=True``. This does not send any code to segment.io,
  but instead plays nicely with the Jinja2 template described below.

- This analytics package sends as much data directly from your server as it
  can, and falls back on supplying events to the browser via the Jinja2 
  template. Below are the examples of identifying and tracking::

    # identify the authenticated user with certain traits (timestamp and 
    # context are optional and described by the segment.io documentation)
    request.analytics.identify(traits, timestamp=None, context=None)

    # identify a (not identified) user with certain traits (timestamp and 
    # context are optional and described by the segment.io documentation)
    request.analytics.identify_foreign(user_id, traits, timestamp=None, 
                                       context=None)

    # track an authenticated user with an event and properties (timestamp and 
    # context are optional and described by the segment.io documentation)
    request.analytics.track(event, properties, timestamp=None, context=None)

    # track a (not identified) user with an event and properties (timestamp and
    # context are optional and described by the segment.io documentation)
    request.analytics.track_foreign(user_id, event, properties, timestamp=None,
                                    context=None)

- When Pyramid fires the ``BeforeRender`` event, pyramid_analytics adds the
  following to the renderer globals::

    analytics: {
       api_token: 'mytoken',
       tracking: {
            alias: userid, // or null if analytics hasn't been told to alias
            events: [{event: 'myevent', 
                        properties: {property1: 'pvalue1'},
                        context: {context1: 'cvalue1'}}]
            identify: userid, // or null
        }
        tracking_json: '...' // the tracking item as json
    }


Jinja2 Integration
------------------
- An easy to use jinja2 template is provided. To use this template, you must
  add pyramid_analytics to your jinja2 search path. If you're using Pyramid's
  pyramid_jinja2, update your config.ini as shown below::

    jinja2.directories =
        pyramid_analytics:templates
        myapp:templates

- To use the template, place this in your templates after including 
  segment.io's javascript::

    {# Segment.io's javascript precedes this... #}
    {% include 'analytics.jinja2' %}

Additional
----------
- For more information, visit `Segment.io's Python Documentation 
  <https://segment.io/libraries/python>`_ and
  `Segment.io's Javascript Documentation 
  <https://segment.io/libraries/analytics.js>`_.
