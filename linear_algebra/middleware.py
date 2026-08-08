from linear_algebra.supabase_client import get_user_from_token

class SupabaseAuthMiddleware:
    """
    Middleware that inspects incoming requests for a Supabase Auth token
    and attaches `request.supabase_user` if valid.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = None
        
        # 1. Check HTTP-only Cookie
        token = request.COOKIES.get("sb_access_token")
        
        # 2. Check Session
        if not token:
            token = request.session.get("sb_access_token")
            
        # 3. Check Authorization Header (for API requests)
        if not token and "HTTP_AUTHORIZATION" in request.META:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1].strip()

        if token:
            user_data = get_user_from_token(token)
            request.supabase_user = user_data
        else:
            request.supabase_user = None

        response = self.get_response(request)
        return response
