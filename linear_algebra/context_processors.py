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

    return {
        "session_user_name": session_user_name,
        "session_user_email": session_user_email,
    }
