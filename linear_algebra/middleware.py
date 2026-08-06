from django.db import connections, DEFAULT_DB_ALIAS
from django.db.utils import OperationalError

class DatabaseResilienceMiddleware:
    """Middleware that catches database connection failures (e.g. unreachable PostgreSQL pooler)
    and gracefully falls back to local SQLite to prevent HTTP 500 errors."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            conn = connections[DEFAULT_DB_ALIAS]
            conn.ensure_connection()
        except Exception as e:
            print("Database connection exception caught by ResilienceMiddleware, switching to SQLite fallback:", e)
            try:
                from django.conf import settings
                settings.DATABASES['default'] = {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': '/tmp/db.sqlite3',
                }
                connections[DEFAULT_DB_ALIAS].close()
            except Exception as inner_e:
                print("Fallback switch error:", inner_e)

        response = self.get_response(request)
        return response
