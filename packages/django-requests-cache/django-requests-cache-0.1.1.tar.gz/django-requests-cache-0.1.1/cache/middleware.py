from django.http import HttpResponse
import redis
import pickle
from . import settings


class CacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        try:
            self.cache = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
        except:
            self.cache = None

    def __call__(self, request):
        if self.cache:
            response = self.cache.get(request.get_full_path())
            if not response:
                response = self.get_response(request)
                data = {
                    'content': response.content,
                    'content_type': response._headers.get('content-type')[1]
                }
                self.cache.set(request.get_full_path(), pickle.dumps(data))
                self.cache.expire(request.get_full_path(), settings.REDIS_EXPIRE)
            else:
                data = pickle.loads(response)
                response = HttpResponse(data.get('content'),
                                        content_type=data.get('content_type'))
        else:
            response = self.get_response(request)
        return response
