import os
import uuid
import inspect
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from .forms import (
    GaussianForm, VectorsForm, GramSchmidtForm, CofactorForm, DiagonalizationForm, GF2Form,
    LoginForm, SignUpForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm
)



from . import math_engine
from .supabase_client import (
    sign_in_user, sign_up_user, sign_out_user,
    reset_password_request, update_user_password,
    update_user_profile, get_supabase_client
)
from .decorators import supabase_login_required

def parse_matrix_input(text):
    """Helper function to parse multiline string of numbers into a 2D list of floats."""
    rows = []
    lines = text.strip().split('\n')
    for line in lines:
        if line.strip():
            row = [float(x) for x in line.strip().split()]
            rows.append(row)
    return rows

def extract_full_name(user, fallback_email=""):
    """Safely pull a display name out of a Supabase user, whether it comes
    back as a dict or as a Supabase User object, falling back to the part
    of the email before the @ if no name is available."""
    full_name = ""
    if isinstance(user, dict):
        full_name = (user.get("user_metadata") or {}).get("full_name", "") or user.get("full_name", "")
    elif user is not None:
        metadata = getattr(user, "user_metadata", None) or {}
        full_name = metadata.get("full_name", "") if isinstance(metadata, dict) else ""
    if not full_name and fallback_email:
        full_name = fallback_email.split("@")[0]
    return full_name

def extract_avatar_url(user):
    """Safely extract avatar_url from a user dict or object."""
    if isinstance(user, dict):
        return (user.get("user_metadata") or {}).get("avatar_url", "") or user.get("avatar_url", "")
    elif user is not None:
        metadata = getattr(user, "user_metadata", None) or {}
        return metadata.get("avatar_url", "") if isinstance(metadata, dict) else getattr(user, "avatar_url", "")
    return ""

import base64
import mimetypes

def save_uploaded_avatar(user_id, uploaded_file):
    """
    Saves an uploaded avatar image file.
    - 1. Attempts Supabase Storage bucket upload if configured.
    - 2. Attempts local disk storage if filesystem is writable (local development).
    - 3. Seamlessly converts to a Base64 Data URL for serverless read-only filesystems (e.g. Vercel).
    """
    if hasattr(uploaded_file, 'seek'):
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
    
    if hasattr(uploaded_file, 'read'):
        file_bytes = uploaded_file.read()
    elif isinstance(uploaded_file, bytes):
        file_bytes = uploaded_file
    else:
        file_bytes = b''
    
    # Guess mime type
    filename = getattr(uploaded_file, 'name', 'avatar.jpg')
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = getattr(uploaded_file, 'content_type', 'image/jpeg') or 'image/jpeg'

    # 1. Try Supabase Storage if available
    client = get_supabase_client()
    if client:
        try:
            clean_id = str(user_id).replace('-', '')[:16]
            ext = os.path.splitext(uploaded_file.name)[1].lower() or '.jpg'
            storage_path = f"avatar_{clean_id}_{uuid.uuid4().hex[:8]}{ext}"
            
            client.storage.from_("avatars").upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            public_url = client.storage.from_("avatars").get_public_url(storage_path)
            if public_url:
                return public_url
        except Exception as storage_err:
            print(f"[Supabase Storage upload fallback]: {storage_err}")

    # 2. Try local filesystem save only if NOT on Vercel / read-only filesystem
    if not os.environ.get('VERCEL') and not os.environ.get('VERCEL_ENV'):
        try:
            avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            os.makedirs(avatars_dir, exist_ok=True)
            
            ext = os.path.splitext(uploaded_file.name)[1].lower() or '.jpg'
            clean_id = str(user_id).replace('-', '')[:16]
            unique_filename = f"avatar_{clean_id}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(avatars_dir, unique_filename)
            
            with open(file_path, 'wb+') as destination:
                destination.write(file_bytes)
                
            return f"{settings.MEDIA_URL.rstrip('/')}/avatars/{unique_filename}"
        except (OSError, PermissionError) as fs_err:
            print(f"[Local filesystem write skipped due to read-only environment]: {fs_err}")

    # 3. Universal serverless & read-only fallback: Base64 Data URL (100% serverless safe)
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(file_bytes))
        img = img.convert('RGB')
        
        # Center square crop
        min_dim = min(img.width, img.height)
        left = (img.width - min_dim) / 2
        top = (img.height - min_dim) / 2
        right = (img.width + min_dim) / 2
        bottom = (img.height + min_dim) / 2
        img = img.crop((left, top, right, bottom))
        img.thumbnail((200, 200), Image.Resampling.LANCZOS)
        
        out_buffer = io.BytesIO()
        img.save(out_buffer, format='JPEG', quality=85)
        file_bytes = out_buffer.getvalue()
        content_type = 'image/jpeg'
    except Exception as pil_err:
        print(f"[Pillow Thumbnail Resizing Note]: {pil_err}")

    encoded_b64 = base64.b64encode(file_bytes).decode('utf-8')
    return f"data:{content_type};base64,{encoded_b64}"





def index_view(request):
    """Renders main public dashboard showing Unit 1 & Unit 2 topics."""
    context = {
        'title': 'Linear Algebra & Data Science Explorer',
        'supabase_user': getattr(request, 'supabase_user', None)
    }
    return render(request, 'linear_algebra/index.html', context)


# ------------------------------------------------------------------------------
# SUPABASE AUTHENTICATION VIEWS
# ------------------------------------------------------------------------------

def login_view(request):
    """User Login via Supabase Auth."""
    if getattr(request, 'supabase_user', None):
        return redirect('linear_algebra:index')

    error = None
    next_url = request.GET.get('next', '')
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        res = sign_in_user(email, password)
        if res['error']:
            error = res['error']
        else:
            # Establish session
            access_token = res['session'].get('access_token', 'demo_access_token_1234') if res['session'] else 'demo_access_token_1234'
            request.session['sb_access_token'] = access_token
            request.session['is_authenticated'] = True
            request.session['user_email'] = email
            user_id = res['user'].get('id', 'demo-user-uuid') if isinstance(res['user'], dict) else getattr(res['user'], 'id', 'demo-user-uuid')
            request.session['user_id'] = user_id
            request.session['user_name'] = extract_full_name(res['user'], fallback_email=email)
            
            user_avatar = extract_avatar_url(res['user'])
            if not user_avatar and user_id:
                try:
                    from .supabase_client import get_user_profile
                    profile = get_user_profile(user_id)
                    if profile:
                        user_avatar = profile.get('avatar_url', '')
                        if profile.get('full_name'):
                            request.session['user_name'] = profile.get('full_name')
                except Exception:
                    pass

            request.session['user_avatar'] = user_avatar
            
            target = next_url if next_url and next_url.startswith('/') else 'linear_algebra:index'
            response = redirect(target)
            # Set HTTP-only secure cookie
            response.set_cookie('sb_access_token', access_token, httponly=True, samesite='Lax', max_age=86400*7)
            return response


    context = {
        'title': 'Sign In • Linear Algebra Explorer',
        'form': form,
        'error': error,
        'next': next_url
    }
    return render(request, 'linear_algebra/login.html', context)

def signup_view(request):
    """User Registration via Supabase Auth."""
    if getattr(request, 'supabase_user', None):
        return redirect('linear_algebra:index')

    error = None
    success_msg = None
    form = SignUpForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        full_name = form.cleaned_data['full_name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        res = sign_up_user(email, password, full_name)
        if res['error']:
            error = res['error']
        else:
            success_msg = "Account created successfully! Please check your email to verify your account or proceed to log in."
            return redirect('linear_algebra:login')

    context = {
        'title': 'Create Account • Linear Algebra Explorer',
        'form': form,
        'error': error,
        'success': success_msg
    }
    return render(request, 'linear_algebra/signup.html', context)

def logout_view(request):
    """Ends Supabase Session and clears cookies."""
    token = request.COOKIES.get('sb_access_token') or request.session.get('sb_access_token')
    sign_out_user(token)
    
    request.session.flush()
    response = redirect('linear_algebra:login')
    response.delete_cookie('sb_access_token')
    return response

def forgot_password_view(request):
    """Requests Password Reset Link via Supabase Auth."""
    error = None
    success_msg = None
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        res = reset_password_request(email)
        if res['error']:
            error = res['error']
        else:
            success_msg = "If an account exists for this email, password recovery instructions have been sent."

    context = {
        'title': 'Reset Password • Linear Algebra Explorer',
        'form': form,
        'error': error,
        'success': success_msg
    }
    return render(request, 'linear_algebra/forgot_password.html', context)

def reset_password_confirm_view(request):
    """Sets new password after user clicks recovery email link."""
    error = None
    success_msg = None
    form = ResetPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        new_password = form.cleaned_data['new_password']
        res = update_user_password(new_password)
        if res['error']:
            error = res['error']
        else:
            success_msg = "Your password has been updated successfully. Please log in with your new password."
            return redirect('linear_algebra:login')

    context = {
        'title': 'Set New Password • Linear Algebra Explorer',
        'form': form,
        'error': error,
        'success': success_msg
    }
    return render(request, 'linear_algebra/reset_password_confirm.html', context)

@supabase_login_required
def profile_view(request):
    """Authenticated User Profile & Account Management."""
    user = getattr(request, 'supabase_user', None) or {}
    error = None
    success_msg = None
    
    current_avatar = request.session.get('user_avatar', '') or (user.get('avatar_url', '') if isinstance(user, dict) else '')
    
    initial_data = {
        'full_name': user.get('full_name', '') if isinstance(user, dict) else '',
        'avatar_url': current_avatar,
    }
    
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, initial=initial_data)

    preset_avatars = [
        {'id': 'avatar-1', 'title': 'Neon Quantum', 'url': '/static/linear_algebra/img/avatars/avatar-1.svg'},
        {'id': 'avatar-2', 'title': 'Cyber Math', 'url': '/static/linear_algebra/img/avatars/avatar-2.svg'},
        {'id': 'avatar-3', 'title': 'Matrix Scholar', 'url': '/static/linear_algebra/img/avatars/avatar-3.svg'},
        {'id': 'avatar-4', 'title': 'Galois Explorer', 'url': '/static/linear_algebra/img/avatars/avatar-4.svg'},
        {'id': 'avatar-5', 'title': 'Gaussian Solver', 'url': '/static/linear_algebra/img/avatars/avatar-5.svg'},
        {'id': 'avatar-6', 'title': 'Eigen Spark', 'url': '/static/linear_algebra/img/avatars/avatar-6.svg'},
    ]

    if request.method == 'POST' and form.is_valid():
        new_name = form.cleaned_data['full_name']
        avatar_preset = form.cleaned_data.get('avatar_preset')
        avatar_url_input = form.cleaned_data.get('avatar_url')
        remove_avatar = form.cleaned_data.get('remove_avatar')

        new_avatar = current_avatar

        if remove_avatar:
            new_avatar = ""
        elif avatar_preset:
            new_avatar = avatar_preset
        elif avatar_url_input:
            new_avatar = avatar_url_input


        if not error:
            # Update session safely without exceeding cookie payload size limits
            request.session['user_name'] = new_name
            try:
                if not new_avatar or not new_avatar.startswith('data:') or len(new_avatar) < 60000:
                    request.session['user_avatar'] = new_avatar
            except Exception as sess_err:
                print(f"[Session Avatar Warning]: {sess_err}")

            current_avatar = new_avatar
            
            # Update user object in memory for current template render
            if isinstance(user, dict):
                user['full_name'] = new_name
                user['avatar_url'] = new_avatar
            
            # Sync with Supabase if connected
            user_id = user.get('id') if isinstance(user, dict) else None
            if user_id and user_id != 'demo-user-uuid-1234':
                token = request.COOKIES.get('sb_access_token') or request.session.get('sb_access_token')
                update_res = update_user_profile(user_id, new_name, new_avatar, access_token=token)
                if not update_res.get('success') and update_res.get('error'):
                    print(f"[Supabase Profile Sync Note]: {update_res['error']}")

            success_msg = "Profile updated successfully! Your changes are saved."



    context = {
        'title': 'User Profile • Account Settings',
        'user': user,
        'form': form,
        'preset_avatars': preset_avatars,
        'current_avatar': current_avatar,
        'error': error,
        'success': success_msg
    }
    return render(request, 'linear_algebra/profile.html', context)


# ------------------------------------------------------------------------------
# PROTECTED MATH SOLVER & VISUALIZER VIEWS (Requires Supabase Auth)
# ------------------------------------------------------------------------------

@supabase_login_required
def gaussian_view(request):
    """Topic 1.1: Systems of Linear Equations & Gaussian Elimination."""
    result = None
    error = None
    form = GaussianForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_gaussian_elimination(matrix_data)
        except Exception as e:
            error = f"Error processing matrix input: {str(e)}"
    else:
        matrix_data = parse_matrix_input(form.fields['matrix_text'].initial)
        result = math_engine.solve_gaussian_elimination(matrix_data)

    code_snippet = inspect.getsource(math_engine.solve_gaussian_elimination)

    context = {
        'title': 'Gaussian Elimination & Row Operations',
        'unit': 'Unit 1 • Topic 1',
        'form': form,
        'result': result,
        'error': error,
        'python_code': code_snippet
    }
    return render(request, 'linear_algebra/gaussian.html', context)

@supabase_login_required
def gf2_view(request):
    """Topic 1.2: Field Axioms via GF(2)."""
    result = math_engine.analyze_gf2_field()
    form = GF2Form(request.POST or None)
    calc_res = None

    if request.method == 'POST' and form.is_valid():
        a = form.cleaned_data['element_a']
        b = form.cleaned_data['element_b']
        op = form.cleaned_data['operation']
        calc_res = math_engine.compute_gf2_calc(a, b, op)
    else:
        calc_res = math_engine.compute_gf2_calc(1, 1, 'add')

    context = {
        'title': 'Field Axioms via GF(2)',
        'unit': 'Unit 1 • Topic 2',
        'result': result,
        'form': form,
        'calc_res': calc_res
    }
    return render(request, 'linear_algebra/gf2.html', context)




@supabase_login_required
def vectors_view(request):
    """Topic 1.3: 3D Vector Dot Product, Cross Product & Projections."""
    result = None
    error = None
    form = VectorsForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        v1 = [form.cleaned_data['v1_x'], form.cleaned_data['v1_y'], form.cleaned_data['v1_z']]
        v2 = [form.cleaned_data['v2_x'], form.cleaned_data['v2_y'], form.cleaned_data['v2_z']]
        try:
            result = math_engine.compute_vector_operations(v1, v2)
        except Exception as e:
            error = f"Error computing vector operations: {str(e)}"
    else:
        v1 = [form.fields['v1_x'].initial, form.fields['v1_y'].initial, form.fields['v1_z'].initial]
        v2 = [form.fields['v2_x'].initial, form.fields['v2_y'].initial, form.fields['v2_z'].initial]
        result = math_engine.compute_vector_operations(v1, v2)

    code_snippet = inspect.getsource(math_engine.compute_vector_operations)

    context = {
        'title': 'Vector Dot Product, Cross Product & Projections',
        'unit': 'Unit 1 • Topic 3',
        'form': form,
        'result': result,
        'error': error,
        'python_code': code_snippet
    }
    return render(request, 'linear_algebra/vectors.html', context)

@supabase_login_required
def gram_schmidt_view(request):
    """Topic 2.1: Gram-Schmidt Orthogonalization Process."""
    result = None
    error = None
    form = GramSchmidtForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        vectors_text = form.cleaned_data['vectors_text']
        try:
            vectors_data = parse_matrix_input(vectors_text)
            result = math_engine.solve_gram_schmidt(vectors_data)
        except Exception as e:
            error = f"Error processing Gram-Schmidt vectors: {str(e)}"
    else:
        vectors_data = parse_matrix_input(form.fields['vectors_text'].initial)
        result = math_engine.solve_gram_schmidt(vectors_data)

    code_snippet = inspect.getsource(math_engine.solve_gram_schmidt)

    context = {
        'title': 'Gram–Schmidt Orthogonalization Process',
        'unit': 'Unit 2 • Topic 1',
        'form': form,
        'result': result,
        'error': error,
        'python_code': code_snippet
    }
    return render(request, 'linear_algebra/gram_schmidt.html', context)

@supabase_login_required
def cofactor_view(request):
    """Topic 2.2: Cofactor Expansion for Determinants."""
    result = None
    error = None
    form = CofactorForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        expand_by = form.cleaned_data['expand_by']
        idx = form.cleaned_data['index'] - 1  # 0-based
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_cofactor_expansion(matrix_data, expand_by, idx)
        except Exception as e:
            error = f"Error calculating Cofactor Expansion: {str(e)}"
    else:
        matrix_data = parse_matrix_input(form.fields['matrix_text'].initial)
        expand_by = form.fields['expand_by'].initial
        idx = form.fields['index'].initial - 1
        result = math_engine.solve_cofactor_expansion(matrix_data, expand_by, idx)

    code_snippet = inspect.getsource(math_engine.solve_cofactor_expansion)

    context = {
        'title': 'Cofactor Expansion for Determinants',
        'unit': 'Unit 2 • Topic 2',
        'form': form,
        'result': result,
        'error': error,
        'python_code': code_snippet
    }
    return render(request, 'linear_algebra/cofactor.html', context)

@supabase_login_required
def diagonalization_view(request):
    """Topic 2.3: Eigenvalues, Eigenvectors & Diagonalization."""
    result = None
    error = None
    form = DiagonalizationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_diagonalization(matrix_data)
        except Exception as e:
            error = f"Error in Diagonalization computation: {str(e)}"
    else:
        matrix_data = parse_matrix_input(form.fields['matrix_text'].initial)
        result = math_engine.solve_diagonalization(matrix_data)

    code_snippet = inspect.getsource(math_engine.solve_diagonalization)

    context = {
        'title': 'Eigenvalues, Eigenvectors & Diagonalization',
        'unit': 'Unit 2 • Topic 3',
        'form': form,
        'result': result,
        'error': error,
        'python_code': code_snippet
    }
    return render(request, 'linear_algebra/diagonalization.html', context)


# ------------------------------------------------------------------------------
# UNIVERSAL PDF EXPORT VIEW (Secured by Supabase Auth)
# ------------------------------------------------------------------------------

@supabase_login_required
def export_pdf_view(request, solver_type):
    """Generates and downloads a clean PDF solution document matching web screenshot layout."""
    from datetime import datetime
    from django.template.loader import render_to_string
    from .pdf_utils import prepare_latex_for_pdf, build_matrix_grid_html, generate_pdf_response

    user = getattr(request, 'supabase_user', None) or {}
    user_email = user.get('email', '') if isinstance(user, dict) else getattr(user, 'email', '')
    
    pdf_steps = []
    final_solution = None
    problem_summary = ""
    unit_badge = "UNIT 1"
    topic_badge = "TOPIC 1.1"
    pdf_title = "Linear Algebra Solution"
    pdf_subtitle = "Step-by-Step Mathematical Derivation"
    pdf_desc = ""
    input_matrix_title = ""
    matrix_grid_html = ""
    input_help_text = ""
    solution_badge = ""
    filename = f"{solver_type}_solution.pdf"

    if solver_type == 'gaussian':
        form = GaussianForm(request.POST or request.GET or None)
        matrix_text = form.cleaned_data['matrix_text'] if form.is_valid() else form.fields['matrix_text'].initial
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_gaussian_elimination(matrix_data)
            unit_badge = "UNIT 1"
            topic_badge = "TOPIC 1.1"
            pdf_title = "Systems of Linear Equations — Gaussian Elimination"
            pdf_subtitle = "Gaussian Elimination & Row Operations"
            pdf_desc = "Row-reduce an augmented matrix step-by-step into Row Echelon Form (REF) & Reduced Row Echelon Form (RREF)."
            input_matrix_title = "Augmented Matrix [A | b]"
            matrix_grid_html = build_matrix_grid_html(matrix_data, is_augmented=True)
            input_help_text = "Enter augmented matrix [A|b] row by row. Separate numbers with spaces."
            solution_badge = result.get('solution_type', 'Unique Solution')
            filename = "Gaussian_Elimination_Solution.pdf"
            
            for step in result.get('steps', []):
                pdf_steps.append({
                    'title': step.get('title', ''),
                    'explanation': step.get('explanation', ''),
                    'rendered_math': prepare_latex_for_pdf(step.get('latex', ''))
                })
            
            final_solution = {
                'summary': result.get('solution_summary', ''),
                'rendered_math': prepare_latex_for_pdf(result.get('solution_latex', ''))
            }
        except Exception as e:
            return HttpResponse(f"Error building PDF for Gaussian Elimination: {e}", status=400)

    elif solver_type == 'gf2':
        result = math_engine.analyze_gf2_field()
        unit_badge = "UNIT 1"
        topic_badge = "TOPIC 1.2"
        pdf_title = "Field Axioms Verification via GF(2)"
        pdf_subtitle = "Binary Galois Field GF(2) Axioms"
        pdf_desc = "Verify the 11 fundamental field axioms for the Galois Binary Field GF(2) = ({0, 1}, +, •)."
        input_matrix_title = "Galois Field GF(2) Elements {0, 1}"
        matrix_grid_html = build_matrix_grid_html([[0, 1], [1, 0]], is_augmented=False)
        input_help_text = "Binary field operations: XOR Addition (+) and AND Multiplication (•)."
        solution_badge = "GF(2) IS A VALID FIELD"
        filename = "GF2_Field_Axioms_Solution.pdf"
        
        for axiom in result.get('axioms', []):
            pdf_steps.append({
                'title': f"{axiom.get('name', '')} ({axiom.get('symbol', '')})",
                'explanation': axiom.get('description', ''),
                'rendered_math': prepare_latex_for_pdf(axiom.get('proof_latex', ''))
            })
            
        final_solution = {
            'summary': "All 11 Field Axioms hold true for GF(2). GF(2) is a valid mathematical field.",
            'rendered_math': prepare_latex_for_pdf(r"\mathbb{F}_2 = (\{0, 1\}, +, \cdot) \text{ is a Field}")
        }

    elif solver_type == 'vectors':
        form = VectorsForm(request.POST or request.GET or None)
        if form.is_valid():
            v1 = [form.cleaned_data['v1_x'], form.cleaned_data['v1_y'], form.cleaned_data['v1_z']]
            v2 = [form.cleaned_data['v2_x'], form.cleaned_data['v2_y'], form.cleaned_data['v2_z']]
        else:
            v1 = [form.fields['v1_x'].initial, form.fields['v1_y'].initial, form.fields['v1_z'].initial]
            v2 = [form.fields['v2_x'].initial, form.fields['v2_y'].initial, form.fields['v2_z'].initial]
        
        try:
            result = math_engine.compute_vector_operations(v1, v2)
            unit_badge = "UNIT 1"
            topic_badge = "TOPIC 1.3"
            pdf_title = "3D Vector Dot Product, Cross Product & Projections"
            pdf_subtitle = "Vector Operations & Geometry"
            pdf_desc = "Compute 3D vector dot product, cross product, magnitudes, angles, and orthogonal projections."
            input_matrix_title = "Input Vectors v1 and v2"
            matrix_grid_html = build_matrix_grid_html([v1, v2], is_augmented=False)
            input_help_text = "3D vectors v1 = [x1, y1, z1] and v2 = [x2, y2, z2]."
            solution_badge = "Orthogonal (v1 ⊥ v2)" if result.get('is_orthogonal') else "Not Orthogonal"
            filename = "Vector_Operations_Solution.pdf"

            pdf_steps = [
                {
                    'title': 'Dot Product & Angle Calculation',
                    'explanation': f"Magnitudes: ||v1|| = {result['mag1']}, ||v2|| = {result['mag2']} | Angle: {result['angle_deg']}° ({result['angle_rad']} rad)",
                    'rendered_math': prepare_latex_for_pdf(f"\\mathbf{{v}}_1 \\cdot \\mathbf{{v}}_2 = {result['dot_prod']}")
                },
                {
                    'title': 'Cross Product Vector & Areas',
                    'explanation': f"Cross Magnitude: {result['cross_mag']} | Parallelepiped Area: {result['parallelepiped_area']} sq units",
                    'rendered_math': prepare_latex_for_pdf(f"\\mathbf{{v}}_1 \\times \\mathbf{{v}}_2 = \\begin{{bmatrix}} {result['cross_prod'][0]} \\\\ {result['cross_prod'][1]} \\\\ {result['cross_prod'][2]} \\end{{bmatrix}}")
                },
                {
                    'title': 'Vector Projection proj_v2(v1)',
                    'explanation': "Orthogonal projection of v1 onto v2",
                    'rendered_math': prepare_latex_for_pdf(f"\\text{{proj}}_{{\\mathbf{{v}}_2}}(\\mathbf{{v}}_1) = \\begin{{bmatrix}} {result['proj_vector'][0]} \\\\ {result['proj_vector'][1]} \\\\ {result['proj_vector'][2]} \\end{{bmatrix}}")
                }
            ]
            
            final_solution = {
                'summary': f"Orthogonal Check: {'YES (v1 ⊥ v2)' if result['is_orthogonal'] else 'NO'}",
                'rendered_math': prepare_latex_for_pdf(f"\\mathbf{{v}}_1 \\cdot \\mathbf{{v}}_2 = {result['dot_prod']}")
            }
        except Exception as e:
            return HttpResponse(f"Error building PDF for Vectors: {e}", status=400)

    elif solver_type == 'gram_schmidt':
        form = GramSchmidtForm(request.POST or request.GET or None)
        vectors_text = form.cleaned_data['vectors_text'] if form.is_valid() else form.fields['vectors_text'].initial
        try:
            vectors_data = parse_matrix_input(vectors_text)
            result = math_engine.solve_gram_schmidt(vectors_data)
            unit_badge = "UNIT 2"
            topic_badge = "TOPIC 2.1"
            pdf_title = "Gram–Schmidt Orthogonalization Process"
            pdf_subtitle = "Vector Space Inner Products & Orthonormal Bases"
            pdf_desc = "Transform a set of linearly independent vectors into an orthonormal basis."
            input_matrix_title = "Input Basis Vectors"
            matrix_grid_html = build_matrix_grid_html(vectors_data, is_augmented=False)
            input_help_text = "Enter linearly independent basis vectors row by row."
            solution_badge = "Orthonormal Basis Verified"
            filename = "Gram_Schmidt_Orthogonalization_Solution.pdf"

            for step in result.get('steps', []):
                pdf_steps.append({
                    'title': f"Vector Step {step.get('step_num', 1)}: Orthogonalizing v_{step.get('step_num', 1)}",
                    'explanation': f"Subtracted projection terms to create orthogonal vector u_{step.get('step_num', 1)}",
                    'rendered_math': f"Orthogonal Vector u_{step.get('step_num', 1)}: <br>{prepare_latex_for_pdf(step.get('u_latex', ''))}<br><br>Normalized Unit Vector e_{step.get('step_num', 1)}:<br>{prepare_latex_for_pdf(step.get('e_latex', ''))}"
                })

            final_solution = {
                'summary': "Orthonormal Basis Verification Matrix (Inner Product Matrix <e_i, e_j>):",
                'rendered_math': prepare_latex_for_pdf(result.get('ortho_check_latex', ''))
            }
        except Exception as e:
            return HttpResponse(f"Error building PDF for Gram-Schmidt: {e}", status=400)

    elif solver_type == 'cofactor':
        form = CofactorForm(request.POST or request.GET or None)
        if form.is_valid():
            matrix_text = form.cleaned_data['matrix_text']
            expand_by = form.cleaned_data['expand_by']
            idx = form.cleaned_data['index'] - 1
        else:
            matrix_text = form.fields['matrix_text'].initial
            expand_by = form.fields['expand_by'].initial
            idx = form.fields['index'].initial - 1

        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_cofactor_expansion(matrix_data, expand_by, idx)
            unit_badge = "UNIT 2"
            topic_badge = "TOPIC 2.2"
            pdf_title = "Cofactor Expansion for Determinants"
            pdf_subtitle = "Matrix Determinants & Submatrix Minors"
            pdf_desc = "Compute matrix determinant via Laplace cofactor expansion along any row or column."
            input_matrix_title = f"Input Square Matrix [A] ({len(matrix_data)}x{len(matrix_data[0])})"
            matrix_grid_html = build_matrix_grid_html(matrix_data, is_augmented=False)
            input_help_text = f"Expansion along {expand_by.capitalize()} {idx + 1}."
            solution_badge = "Determinant Calculated"
            filename = "Cofactor_Expansion_Determinant_Solution.pdf"

            for term in result.get('terms', []):
                pdf_steps.append({
                    'title': f"Term {term.get('row', 1)},{term.get('col', 1)}: Entry a = {term.get('entry', 0)}",
                    'explanation': f"Submatrix Minor det(M) = {term.get('minor_det', 0)} | Cofactor C = {term.get('cofactor', 0)}",
                    'rendered_math': f"Minor Matrix M:<br>{prepare_latex_for_pdf(term.get('minor_matrix_latex', ''))}<br><br>Cofactor Calculation:<br>{prepare_latex_for_pdf(term.get('cofactor_latex', ''))}"
                })

            final_solution = {
                'summary': "Total Matrix Determinant det(A):",
                'rendered_math': prepare_latex_for_pdf(f"\\det(A) = {result.get('total_det_latex', '')}")
            }
        except Exception as e:
            return HttpResponse(f"Error building PDF for Cofactor Expansion: {e}", status=400)

    elif solver_type == 'diagonalization':
        form = DiagonalizationForm(request.POST or request.GET or None)
        matrix_text = form.cleaned_data['matrix_text'] if form.is_valid() else form.fields['matrix_text'].initial
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_diagonalization(matrix_data)
            unit_badge = "UNIT 2"
            topic_badge = "TOPIC 2.3"
            pdf_title = "Eigenvalues, Eigenvectors & Diagonalization"
            pdf_subtitle = "Spectral Theory & Matrix Decomposition"
            pdf_desc = "Compute matrix eigenvalues, eigenspace basis vectors, and spectral decomposition A = P D P⁻¹."
            input_matrix_title = f"Input Square Matrix [A] ({len(matrix_data)}x{len(matrix_data[0])})"
            matrix_grid_html = build_matrix_grid_html(matrix_data, is_augmented=False)
            input_help_text = "Enter square matrix [A] row by row. Separate numbers with spaces."
            solution_badge = "MATRIX IS DIAGONALIZABLE" if result.get('is_diagonalizable') else "NOT DIAGONALIZABLE"
            filename = "Matrix_Diagonalization_Solution.pdf"

            # Section 1
            pdf_steps.append({
                'title': 'Section 1: Characteristic Polynomial det(A - λI) = 0',
                'explanation': 'Roots of characteristic polynomial yield matrix eigenvalues',
                'rendered_math': prepare_latex_for_pdf(f"p(\\lambda) = {result.get('char_poly_latex', '')} = 0")
            })

            # Section 2
            eig_details = []
            for item in result.get('eigenvalues_summary', []):
                eig_details.append(f"Eigenvalue λ = {item.get('eigenvalue_latex', '')} (Alg Mult: {item.get('alg_mult', 1)}, Geom Mult: {item.get('geom_mult', 1)})")
            
            pdf_steps.append({
                'title': 'Section 2: Eigenvalues & Eigenspaces',
                'explanation': "<br>".join(eig_details),
                'rendered_math': prepare_latex_for_pdf(f"P = {result.get('P_latex', '')}")
            })

            # Section 3
            if result.get('is_diagonalizable'):
                pdf_steps.append({
                    'title': 'Section 3: Matrix Decomposition A = P D P⁻¹',
                    'explanation': 'Modal Matrix P and Diagonal Matrix D',
                    'rendered_math': f"Modal Matrix P:<br>{prepare_latex_for_pdf(result.get('P_latex', ''))}<br><br>Diagonal Matrix D:<br>{prepare_latex_for_pdf(result.get('D_latex', ''))}"
                })
                final_solution = {
                    'summary': "MATRIX IS DIAGONALIZABLE (A = P D P⁻¹)",
                    'rendered_math': prepare_latex_for_pdf(f"P = {result.get('P_latex', '')}, D = {result.get('D_latex', '')}")
                }
            else:
                final_solution = {
                    'summary': "MATRIX IS NOT DIAGONALIZABLE (Geometric multiplicity is less than algebraic multiplicity)",
                    'rendered_math': ""
                }
        except Exception as e:
            return HttpResponse(f"Error building PDF for Diagonalization: {e}", status=400)

    else:
        from django.http import Http404
        raise Http404("Invalid solver type specified.")

    context = {
        'unit_badge': unit_badge,
        'topic_badge': topic_badge,
        'pdf_title': pdf_title,
        'pdf_subtitle': pdf_subtitle,
        'pdf_desc': pdf_desc,
        'input_matrix_title': input_matrix_title,
        'matrix_grid_html': matrix_grid_html,
        'input_help_text': input_help_text,
        'solution_badge': solution_badge,
        'export_timestamp': datetime.now().strftime("%m/%d/%y, %I:%M %p"),
        'user_email': user_email,
        'problem_summary': problem_summary,
        'pdf_steps': pdf_steps,
        'final_solution': final_solution,
    }

    rendered_html = render_to_string('linear_algebra/pdf_export.html', context)
    return generate_pdf_response(rendered_html, filename=filename)

