import logging

from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_safe

logger = logging.getLogger(__name__)


@require_safe
def healthz(request: HttpRequest) -> HttpResponse:
    """Smoke test endpoint for health checks or uptime monitoring.

    Runs a trivial database round-trip so a 200 proves the full stack
    (gunicorn -> Django -> ORM -> database) is working. Any failure is
    allowed to propagate as a 500.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return HttpResponse("ok", content_type="text/plain")


@require_safe
def sentry_debugz(request: HttpRequest) -> HttpResponse:
    logger.info("Info log")
    logger.warning("Warning log")
    division_by_zero = 1 / 0
    return HttpResponse(division_by_zero, content_type="text/plain")
