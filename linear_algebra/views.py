import inspect
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import (
    GaussianForm, VectorsForm, GramSchmidtForm, CofactorForm, DiagonalizationForm, GF2Form,
    LoginForm, SignUpForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm
)

from . import math_engine
from .supabase_client import (
    sign_in_user, sign_up_user, sign_out_user,
    reset_password_request, update_user_password
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
            request.session['user_id'] = res['user'].get('id', 'demo-user-uuid') if isinstance(res['user'], dict) else getattr(res['user'], 'id', 'demo-user-uuid')
            request.session['user_name'] = extract_full_name(res['user'], fallback_email=email)
            
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
    user = getattr(request, 'supabase_user', None)
    error = None
    success_msg = None
    
    initial_data = {'full_name': user.get('full_name', '') if user else ''}
    form = ProfileUpdateForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        new_name = form.cleaned_data['full_name']
        if user:
            user['full_name'] = new_name
            request.session['user_name'] = new_name
            success_msg = "Profile information updated successfully!"

    context = {
        'title': 'User Profile • Account Settings',
        'user': user,
        'form': form,
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
