from django.conf import settings
from http import HTTPStatus

ENABLE_REDIS_CACHE = getattr(settings, "ENABLE_REDIS_CACHE", None)
REDIS_HOST = getattr(settings, "REDIS_HOST", 'localhost')
REDIS_PORT = getattr(settings, "REDIS_PORT", 6379)
REDIS_DB = getattr(settings, "REDIS_DB", 0)
REDIS_EXPIRE = getattr(settings, "REDIS_EXPIRE", 600)
REDIS_STATUS_CODE_ALLOWED = getattr(
    settings, "REDIS_STATUS_CODE_ALLOWED",
    ','.join(
        [str(HTTPStatus.OK),
         str(HTTPStatus.CREATED),
         str(HTTPStatus.ACCEPTED),
         str(HTTPStatus.NON_AUTHORITATIVE_INFORMATION),
         str(HTTPStatus.NO_CONTENT),
         str(HTTPStatus.RESET_CONTENT),
         str(HTTPStatus.PARTIAL_CONTENT),
         str(HTTPStatus.MULTI_STATUS)]
    )
)
