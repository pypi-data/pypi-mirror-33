from django.http import HttpResponse
import redis
import pickle
from . import settings
import os
import logging
import json


def logging_es(cache_key, cache_value, force_log=False):
    """ES logging."""
    prefix = settings.REDIS_CACHE_PREFIX
    cache_name = '{} {}'.format(prefix, 'django cache') if prefix else 'django cache'
    environment = os.environ.get('DJANGO_SETTINGS_MODULE', 'production')
    environment = environment.lstrip('config.settings').lower()
    if environment != 'test' and (force_log or settings.DEBUG or environment == 'development'):
        logger = logging.getLogger('django-requests-cache')
        cache_value = {
            'content': json.loads(cache_value.get('content')),
            'content_type': cache_value.get('content_type'),
        }
        logger.debug(
            cache_name,
            extra={
                "cache_key": cache_key,
                "cache_value": cache_value,
            }
        )


class CacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        if settings.ENABLE_REDIS_CACHE:
            self.cache = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
                socket_keepalive=settings.REDIS_SOCKET_KEEPALIVE,
                socket_keepalive_options=settings.REDIS_SOCKET_KEEPALIVE_OPTIONS,
                connection_pool=settings.REDIS_CONNECTION_POOL,
                unix_socket_path=settings.REDIS_UNIX_SOCKET_PATH,
                encoding=settings.REDIS_ENCODING,
                encoding_errors=settings.REDIS_ENCODING_ERRORS,
                charset=settings.REDIS_CHARSET,
                errors=settings.REDIS_ERRORS,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                ssl=settings.REDIS_SSL,
                ssl_keyfile=settings.REDIS_SSL_KEYFILE,
                ssl_certfile=settings.REDIS_SSL_CERTFILE,
                ssl_cert_reqs=settings.REDIS_SSL_CERT_REQS,
                ssl_ca_certs=settings.REDIS_SSL_CA_CERTS,
                max_connections=settings.REDIS_MAX_CONNECTIONS
            )
            self.cache.info()
        else:
            self.cache = None

    def __call__(self, request):
        if self.cache:
            prefix = settings.REDIS_CACHE_PREFIX
            full_path = request.get_full_path()
            cache_key = '{}:{}'.format(prefix, full_path) if prefix else full_path
            response = self.cache.get(cache_key)
            if not response:
                response = self.get_response(request)
                if str(response.status_code) in settings.REDIS_STATUS_CODE_ALLOWED:
                    data = {
                        'content': response.content,
                        'content_type': response._headers.get('content-type')[1]
                    }
                    self.cache.set(cache_key, pickle.dumps(data))
                    self.cache.expire(cache_key, settings.REDIS_EXPIRE)
                    if settings.CACHE_LOGSTASH:
                        logging_es(cache_key, data)
            else:
                data = pickle.loads(response)
                response = HttpResponse(data.get('content'),
                                        content_type=data.get('content_type'))
        else:
            response = self.get_response(request)
        return response
