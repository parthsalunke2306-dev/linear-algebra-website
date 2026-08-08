from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse

def supabase_login_required(view_func):
    """
    Decorator for views that require Supabase authentication.
    Redirects unauthenticated browser requests to /login/
    and returns 401 JSON response for API requests.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        supabase_user = getattr(request, "supabase_user", None)
        
        # Also check session fallback
        if not supabase_user and request.session.get("is_authenticated"):
            supabase_user = {
                "id": request.session.get("user_id", "demo-user-uuid-1234"),
                "email": request.session.get("user_email", "scholar@datascience.edu"),
                "full_name": request.session.get("user_name", "Data Science Scholar")
            }
            request.supabase_user = supabase_user

        if not supabase_user:
            # If request expects JSON or is AJAX API request
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("accept", ""):
                return JsonResponse({"error": "Authentication required. Please log in to access this feature."}, status=401)
            
            # Redirect browser request to login with next parameter
            current_path = request.get_full_path()
            return redirect(f"/login/?next={current_path}")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
