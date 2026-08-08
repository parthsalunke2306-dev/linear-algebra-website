from linear_algebra.supabase_client import get_user_from_token

class SupabaseAuthMiddleware:
    """
    Middleware that inspects incoming requests for a Supabase Auth token
    and attaches `request.supabase_user` if valid.
    Fails safely without raising server errors.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.supabase_user = None
        try:
            token = None
            
            # 1. Check HTTP-only Cookie
            if hasattr(request, 'COOKIES'):
                token = request.COOKIES.get("sb_access_token")
            
            # 2. Check Session
            if not token and hasattr(request, 'session'):
                try:
                    token = request.session.get("sb_access_token")
                except Exception:
                    pass
                
            # 3. Check Authorization Header (for API requests)
            if not token and hasattr(request, 'META') and "HTTP_AUTHORIZATION" in request.META:
                auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header.split("Bearer ")[1].strip()

            if token:
                user_data = get_user_from_token(token)
                request.supabase_user = user_data
        except Exception as e:
            print(f"[Supabase Middleware Warning]: {e}")
            request.supabase_user = None

        response = self.get_response(request)
        return response
