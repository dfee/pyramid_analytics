pyramid_analytics
=================

Segment.io initializer for the Pyramid Web Framework. 100% Test Covered.

- The following configuration options are required in your config.ini::

    pyramid.includes =
        pyramid_analytics

    analytics.secret = mysekret
    analytics.flush_at = 20
    analytics.flush_after = 10
    analytics.async = True
    analytics.send = True
    analytics.max_queue_size = 100000
  
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
  
- All other options are detailed at url: https://segment.io/libraries/python
