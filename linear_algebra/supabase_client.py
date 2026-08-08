import os
import jwt
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_supabase_client: Client | None = None

def get_supabase_client() -> Client | None:
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
    """
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
    """
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

def get_user_from_token(token: str):
    """
    Validates token and returns user identity.
    Note: the "demo_access_token_1234" placeholder (used when no Supabase
    credentials are configured) is handled directly in SupabaseAuthMiddleware
    from session data, since a bare token string carries no per-user info.
    """
    client = get_supabase_client()
    if client and token:
        try:
            res = client.auth.get_user(token)
            if res and res.user:
                user_meta = getattr(res.user, "user_metadata", {}) or {}
                return {
                    "id": res.user.id,
                    "email": res.user.email,
                    "full_name": user_meta.get("full_name", res.user.email.split("@")[0].title())
                }
        except Exception:
            pass
    return None
