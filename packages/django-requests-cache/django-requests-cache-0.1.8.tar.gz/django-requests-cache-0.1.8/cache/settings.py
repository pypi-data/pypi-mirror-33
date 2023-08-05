from django.conf import settings
from http import HTTPStatus

ENABLE_REDIS_CACHE = getattr(settings, "ENABLE_REDIS_CACHE", None)
REDIS_CACHE_PREFIX = getattr(settings, "REDIS_CACHE_PREFIX", None)

REDIS_HOST = getattr(settings, "REDIS_HOST", 'localhost')
REDIS_PORT = getattr(settings, "REDIS_PORT", 6379)
REDIS_DB = getattr(settings, "REDIS_DB", 0)
REDIS_PASSWORD = getattr(settings, "REDIS_PASSWORD", None)
REDIS_SOCKET_TIMEOUT = getattr(settings, "REDIS_SOCKET_TIMEOUT", None)
REDIS_SOCKET_CONNECT_TIMEOUT = getattr(
    settings, "REDIS_SOCKET_CONNECT_TIMEOUT", None)
REDIS_SOCKET_KEEPALIVE = getattr(settings, "REDIS_SOCKET_KEEPALIVE", None)
REDIS_SOCKET_KEEPALIVE_OPTIONS = getattr(
    settings, "REDIS_SOCKET_KEEPALIVE_OPTIONS", None)
REDIS_CONNECTION_POOL = getattr(settings, "REDIS_CONNECTION_POOL", None)
REDIS_UNIX_SOCKET_PATH = getattr(settings, "REDIS_UNIX_SOCKET_PATH", None)
REDIS_ENCODING = getattr(settings, "REDIS_ENCODING", "utf-8")
REDIS_ENCODING_ERRORS = getattr(settings, "REDIS_ENCODING_ERRORS", "strict")
REDIS_CHARSET = getattr(settings, "REDIS_CHARSET", None)
REDIS_ERRORS = getattr(settings, "REDIS_ERRORS", None)
REDIS_DECODE_RESPONSES = getattr(settings, "REDIS_DECODE_RESPONSES", None)
REDIS_RETRY_ON_TIMEOUT = getattr(settings, "REDIS_RETRY_ON_TIMEOUT", None)
REDIS_SSL = getattr(settings, "REDIS_SSL", None)
REDIS_SSL_KEYFILE = getattr(settings, "REDIS_SSL_KEYFILE", None)
REDIS_SSL_CERTFILE = getattr(settings, "REDIS_SSL_CERTFILE", None)
REDIS_SSL_CERT_REQS = getattr(settings, "REDIS_SSL_CERT_REQS", None)
REDIS_SSL_CA_CERTS = getattr(settings, "REDIS_SSL_CA_CERTS", None)
REDIS_MAX_CONNECTIONS = getattr(settings, "REDIS_MAX_CONNECTIONS", None)

REDIS_EXPIRE = getattr(settings, "REDIS_EXPIRE", 600)

REDIS_STATUS_CODE_ALLOWED = getattr(
    settings,
    "REDIS_STATUS_CODE_ALLOWED",
    [str(HTTPStatus.OK),
     str(HTTPStatus.CREATED),
     str(HTTPStatus.ACCEPTED),
     str(HTTPStatus.NON_AUTHORITATIVE_INFORMATION),
     str(HTTPStatus.NO_CONTENT),
     str(HTTPStatus.RESET_CONTENT),
     str(HTTPStatus.PARTIAL_CONTENT),
     str(HTTPStatus.MULTI_STATUS)]
)
