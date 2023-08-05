import logging
from django.db import connection
from django.conf import settings
_logger = logging.getLogger(__name__)

class SqlInspectorMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.ENABLE_SQL_INSPECTOR:
            sqltime = 0
            for query in connection.queries:
                sqltime += float(query['time'])
            _logger.info("SQL PERFORMANCE INSPECTOR: Page render: {0} sec. for {1} queries.".format(
                sqltime, len(connection.queries)))
        return response