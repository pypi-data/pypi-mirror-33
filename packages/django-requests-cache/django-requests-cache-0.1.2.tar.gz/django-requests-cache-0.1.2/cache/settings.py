from django.conf import settings

REDIS_HOST = getattr(settings, "REDIS_HOST", 'localhost')
REDIS_PORT = getattr(settings, "REDIS_PORT", 6379)
REDIS_DB = getattr(settings, "REDIS_DB", 0)
REDIS_EXPIRE = getattr(settings, "REDIS_EXPIRE", 600)
