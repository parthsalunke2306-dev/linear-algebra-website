import os
try:
    import jwt
except ImportError:
    jwt = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

from django.conf import settings

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_supabase_client = None

def is_email_authorized(email: str) -> bool:
    """
    Checks if an email address is authorized to register or access the application.
    Rejects unauthorized domains (e.g. @parth.com or non-approved email addresses).
    """
    if not email or not isinstance(email, str):
        return False
    
    clean_email = email.strip().lower()
    if "@" not in clean_email:
        return False
    
    domain = "@" + clean_email.split("@")[-1]

    # Explicitly block unauthorized test/fake domains
    unauthorized_domains = ['@parth.com', '@fake.com', '@test.com', '@temp.com', '@mailinator.com', '@dispostable.com']
    if domain in unauthorized_domains:
        return False

    try:
        if getattr(settings, 'ENABLE_EMAIL_WHITELIST', True):
            exact_allowed = getattr(settings, 'ALLOWED_EXACT_EMAILS', [])
            domain_allowed = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [])

            # Check exact list first if specified
            if exact_allowed and clean_email in [e.lower() for e in exact_allowed]:
                return True

            # Check domain list
            if domain_allowed:
                for d in domain_allowed:
                    if clean_email.endswith(d.lower()):
                        return True
                return False
    except Exception:
        pass

    return True

def get_supabase_client():
    """
    Returns the Supabase Client instance if credentials are valid.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    
    if SUPABASE_URL and SUPABASE_ANON_KEY and not SUPABASE_URL.startswith("https://your-supabase"):
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            return _supabase_client
        except Exception as e:
            print(f"[Supabase Client Error] Failed to initialize: {e}")
            return None
    return None

def sign_up_user(email: str, password: str, full_name: str):
    """
    Registers a new user via Supabase Auth and creates their application profile.
    Enforces Email Authorization restrictions.
    """
    if not is_email_authorized(email):
        return {
            "user": None,
            "session": None,
            "error": f"Access Denied: The email address '{email}' is not authorized to register for this application."
        }

    client = get_supabase_client()

    if not client:
        # Fallback local demo session if credentials not set yet
        return {
            "user": {
                "id": "demo-user-uuid-1234",
                "email": email,
                "user_metadata": {"full_name": full_name}
            },
            "session": {"access_token": "demo_access_token_1234"},
            "error": None
        }
    
    try:
        res = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })
        if res.user:
            # Create user profile record in public.profiles table
            try:
                client.table("profiles").upsert({
                    "id": res.user.id,
                    "full_name": full_name,
                    "avatar_url": ""
                }).execute()
            except Exception as profile_err:
                print(f"[Profile Upsert Warning]: {profile_err}")
                
        return {"user": res.user, "session": res.session, "error": None}
    except Exception as e:
        return {"user": None, "session": None, "error": str(e)}

def sign_in_user(email: str, password: str):
    """
    Authenticates user using Supabase Auth.
    Enforces Email Authorization restrictions.
    """
    if not is_email_authorized(email):
        return {
            "user": None,
            "session": None,
            "error": f"Access Denied: The email address '{email}' is not authorized to log into this application."
        }

    client = get_supabase_client()

    if not client:
        # Fallback local demo auth
        if email and password:
            return {
                "user": {
                    "id": "demo-user-uuid-1234",
                    "email": email,
                    "user_metadata": {"full_name": email.split("@")[0]}
                },
                "session": {"access_token": "demo_access_token_1234"},
                "error": None
            }
        return {"user": None, "session": None, "error": "Invalid email or password."}
    
    try:
        res = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {"user": res.user, "session": res.session, "error": None}
    except Exception as e:
        return {"user": None, "session": None, "error": str(e)}

def sign_out_user(access_token: str | None = None):
    """
    Ends the Supabase session.
    """
    client = get_supabase_client()
    if client:
        try:
            client.auth.sign_out()
        except Exception:
            pass
    return True

def reset_password_request(email: str):
    """
    Sends password reset email via Supabase Auth.
    """
    client = get_supabase_client()
    if not client:
        return {"success": True, "error": None}
    try:
        client.auth.reset_password_for_email(email)
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_user_password(new_password: str):
    """
    Updates the authenticated user's password.
    """
    client = get_supabase_client()
    if not client:
        return {"success": True, "error": None}
    try:
        client.auth.update_user({"password": new_password})
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_user_profile(user_id: str, full_name: str, avatar_url: str = "", access_token: str | None = None):
    """
    Updates the authenticated user's profile metadata in Supabase (public.profiles & auth user metadata).
    """
    client = get_supabase_client()
    if not client:
        return {"success": True, "error": None}
    
    errors = []
    if access_token and access_token != "demo_access_token_1234":
        try:
            client.auth.set_session(access_token, "")
        except Exception:
            pass

    try:
        # Update user metadata
        client.auth.update_user({
            "data": {
                "full_name": full_name,
                "avatar_url": avatar_url
            }
        })
    except Exception as e:
        errors.append(f"Auth metadata update: {e}")

    try:
        # Update public.profiles table
        client.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "avatar_url": avatar_url
        }).execute()
    except Exception as e:
        errors.append(f"Profiles table upsert: {e}")

    if errors:
        return {"success": False, "error": "; ".join(errors)}
    return {"success": True, "error": None}

def get_user_profile(user_id: str):
    """
    Retrieves user profile data from public.profiles table if available.
    """
    client = get_supabase_client()
    if client and user_id:
        try:
            res = client.table("profiles").select("*").eq("id", user_id).single().execute()
            if res and res.data:
                return res.data
        except Exception:
            pass
    return None

def get_user_from_token(token: str):
    """
    Validates token and returns user identity with avatar.
    """
    client = get_supabase_client()
    if client and token:
        try:
            res = client.auth.get_user(token)
            if res and res.user:
                user_meta = getattr(res.user, "user_metadata", {}) or {}
                avatar_url = user_meta.get("avatar_url", "")
                full_name = user_meta.get("full_name", "")
                
                # Check profiles table for avatar or name if missing
                if not avatar_url or not full_name:
                    profile = get_user_profile(res.user.id)
                    if profile:
                        if not avatar_url:
                            avatar_url = profile.get("avatar_url", "")
                        if not full_name:
                            full_name = profile.get("full_name", "")

                return {
                    "id": res.user.id,
                    "email": res.user.email,
                    "full_name": full_name or res.user.email.split("@")[0].title(),
                    "avatar_url": avatar_url
                }
        except Exception:
            pass
    return None


