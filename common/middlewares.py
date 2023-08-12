import logging

from django.db import connection

logger = logging.getLogger(__name__)


class DBStatsMiddleware:
    """Middleware class to add number of SQL queries to headers."""

    def __init__(self, get_response):  # noqa: D107
        self.get_response = get_response

    def __call__(self, request):
        """Get the number of SQL queries from django and pass it to header."""
        response = self.get_response(request)
        connection.force_debug_cursor = True
        total_count = len(connection.queries)

        if total_count >= 100:
            status = "CRITICAL"
        elif 100 > total_count > 30:
            status = "WARNING"
        elif 30 >= total_count > 20:
            status = "MODERATE"
        else:
            status = "OK"

        logger.info(
            "[DBSTAT %s] %d db queries on path %s", status, total_count, request.path
        )

        response["X-DB-TC"] = total_count

        return response
