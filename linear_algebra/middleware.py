from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management import call_command

class DatabaseResilienceMiddleware:
    """Middleware that catches database connection failures (e.g. unreachable PostgreSQL pooler)
    and gracefully falls back to local SQLite with complete table auto-migration to prevent HTTP 500 errors."""
    
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
                fallback_db = {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': '/tmp/db.sqlite3',
                    'ATOMIC_REQUESTS': False,
                    'AUTOCOMMIT': True,
                    'CONN_MAX_AGE': 0,
                    'CONN_HEALTH_CHECKS': False,
                    'OPTIONS': {},
                    'TIME_ZONE': None,
                    'USER': '',
                    'PASSWORD': '',
                    'HOST': '',
                    'PORT': '',
                }
                settings.DATABASES['default'] = fallback_db
                connections[DEFAULT_DB_ALIAS].close()

                # Automatically migrate SQLite fallback database so auth_user and all tables exist instantly
                try:
                    call_command('migrate', interactive=False)
                except Exception as m_err:
                    print("Fallback migration error:", m_err)
            except Exception as inner_e:
                print("Fallback switch error:", inner_e)

        response = self.get_response(request)
        return response
