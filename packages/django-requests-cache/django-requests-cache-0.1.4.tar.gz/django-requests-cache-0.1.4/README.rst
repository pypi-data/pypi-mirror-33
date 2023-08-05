=====
Django request cache
=====

Middlewares:
-----------

 - CacheMiddleware


Use:
----

.. code-block:: python

   # settings.py
   INSTALLED_APPS = [
       # .
       # .
       # .
       "cache.apps.CacheConfig"
   ]


   MIDDLEWARE = [
       'cache.middleware.CacheMiddleware',
       # .
       # .
       # .
   ]

   REDIS_HOST = 'localhost'
   REDIS_PORT = 6379
   REDIS_DB = 0
   REDIS_EXPIRE = 600
