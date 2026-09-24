from functools import wraps

def supabase_login_required(view_func):
    """
    Decorator for views that previously required authentication.
    Passes through directly to allow all visitors immediate access to all solvers
    without redirecting to login.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

