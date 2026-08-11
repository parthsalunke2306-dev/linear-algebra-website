def user_display(request):
    """
    Exposes safe, always-present display values derived from the session.

    Template code must never do `request.session.user_name`-style dotted
    lookups: when the key is absent, Django's SessionStore raises inside a
    filter argument (e.g. `|default:request.session.user_name`) and that
    exception is NOT silenced the way a normal failed variable lookup is,
    because Django resolves filter *arguments* without the try/except that
    protects the main variable. That produces a hard 500 (VariableDoesNotExist)
    instead of an empty string. Precomputing plain, always-defined context
    variables here avoids the whole class of bug.
    """
    session = getattr(request, "session", None)
    session_user_name = session.get("user_name", "") if session else ""
    session_user_email = session.get("user_email", "") if session else ""
    session_user_avatar = session.get("user_avatar", "") if session else ""

    # Also check if attached to request.supabase_user
    supabase_user = getattr(request, "supabase_user", None)
    if supabase_user and isinstance(supabase_user, dict):
        if not session_user_avatar and supabase_user.get("avatar_url"):
            session_user_avatar = supabase_user.get("avatar_url", "")

    return {
        "session_user_name": session_user_name,
        "session_user_email": session_user_email,
        "session_user_avatar": session_user_avatar,
    }

