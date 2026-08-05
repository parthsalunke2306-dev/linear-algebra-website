from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .forms import (
    UserSignUpForm, UserLoginForm, UserProfileForm, UserPasswordChangeForm,
    PasswordResetRequestForm, SetNewPasswordForm,
    GaussianForm, VectorsForm, GramSchmidtForm, CofactorForm, DiagonalizationForm
)
from .models import SiteSetting, TopicModule, UserCalculationHistory
from . import math_engine

def parse_matrix_input(text):
    """Helper function to parse multiline string of numbers into a 2D list of floats."""
    rows = []
    lines = text.strip().split('\n')
    for line in lines:
        if line.strip():
            row = [float(x) for x in line.strip().split()]
            rows.append(row)
    return rows

def ensure_default_data(request=None):
    """Seeds SiteSetting, default TopicModules, and Admin account if database is empty or tables don't exist yet."""
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        print("Migrate exception in ensure_default_data:", e)

    # Auto-seed default Admin Superuser Account
    try:
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@linearalgebra.app', 'admin123')
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'User'
            admin_user.save()
        else:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
    except Exception as e:
        print("Admin user auto-seed error:", e)

    # Serverless resilience: Auto-provision user from signed session cookie if ephemeral SQLite db was reset
    if request and hasattr(request, 'session') and hasattr(request, 'user') and not request.user.is_authenticated:
        session_username = request.session.get('auth_username')
        session_email = request.session.get('auth_email')
        if session_username:
            try:
                user, created = User.objects.get_or_create(
                    username=session_username,
                    defaults={
                        'email': session_email or f"{session_username}@example.com",
                        'first_name': request.session.get('auth_first_name', '')
                    }
                )
                login(request, user)
            except Exception as e:
                print("Serverless auto-login error:", e)

    try:
        site_settings, _ = SiteSetting.objects.get_or_create()

        if TopicModule.objects.count() == 0:
            default_topics = [
                {
                    'slug': 'gaussian',
                    'topic_code': 'TOPIC 1.1',
                    'title': 'Gaussian Elimination',
                    'unit': 'UNIT 1',
                    'description': 'Row-reduce an augmented matrix step-by-step into Row Echelon Form (REF) & RREF.',
                    'icon_class': 'bi-grid-3x3',
                    'icon_color_class': 'text-info',
                    'display_order': 1,
                },
                {
                    'slug': 'gf2',
                    'topic_code': 'TOPIC 1.2',
                    'title': 'Field Axioms GF(2)',
                    'unit': 'UNIT 1',
                    'description': 'Explore 2-element Galois Field F_2 = {0, 1} with addition and multiplication mod 2.',
                    'icon_class': 'bi-shield-check',
                    'icon_color_class': 'text-warning',
                    'display_order': 2,
                },
                {
                    'slug': 'vectors',
                    'topic_code': 'TOPIC 1.3',
                    'title': 'Dot & Cross Product',
                    'unit': 'UNIT 1',
                    'description': 'Calculate 3D vector dot products, cross products, angles, projections, and 3D orbit graphics.',
                    'icon_class': 'bi-compass',
                    'icon_color_class': 'text-success',
                    'display_order': 3,
                },
                {
                    'slug': 'gram_schmidt',
                    'topic_code': 'TOPIC 2.1',
                    'title': 'Gram–Schmidt',
                    'unit': 'UNIT 2',
                    'description': 'Convert linearly independent vectors into an orthogonal and orthonormal basis.',
                    'icon_class': 'bi-bezier2',
                    'icon_color_class': 'text-info',
                    'display_order': 4,
                },
                {
                    'slug': 'cofactor',
                    'topic_code': 'TOPIC 2.2',
                    'title': 'Cofactor Expansion',
                    'unit': 'UNIT 2',
                    'description': 'Calculate matrix determinants along any row or column using sign checkerboards.',
                    'icon_class': 'bi-diagram-3',
                    'icon_color_class': 'text-purple',
                    'display_order': 5,
                },
                {
                    'slug': 'diagonalization',
                    'topic_code': 'TOPIC 2.3',
                    'title': 'Diagonalization',
                    'unit': 'UNIT 2',
                    'description': 'Calculate characteristic polynomial, eigenvalues, eigenspaces, and matrix decomposition A = PDP^-1.',
                    'icon_class': 'bi-gem',
                    'icon_color_class': 'text-danger',
                    'display_order': 6,
                },
            ]
            for topic in default_topics:
                TopicModule.objects.get_or_create(slug=topic['slug'], defaults=topic)

        return site_settings
    except Exception as e:
        print("Database seed fallback error:", e)
        return SiteSetting(
            site_title="Linear Algebra & Field Theory Explorer",
            hero_subtitle="Interactive step-by-step LaTeX matrix solvers, 3D vector graphics, dynamic matrix resizers, Light/Dark theme toggle, and LaTeX formula copy.",
            curriculum_badge="DATA SCIENCE MATHEMATICS CURRICULUM"
        )

def get_safe_site_settings(request=None):
    """Safely retrieves SiteSetting without raising DB errors."""
    return ensure_default_data(request)


# PUBLIC VIEWS
def public_index_view(request):
    """Public landing page displaying website branding, introduction, feature overviews, and Sign In / Sign Up CTAs."""
    site_settings = get_safe_site_settings(request)

    try:
        unit1_topics = list(TopicModule.objects.filter(unit='UNIT 1', is_active=True))
        unit2_topics = list(TopicModule.objects.filter(unit='UNIT 2', is_active=True))
    except Exception:
        unit1_topics = []
        unit2_topics = []

    context = {
        'title': getattr(site_settings, 'site_title', "Linear Algebra & Field Theory Explorer"),
        'site_settings': site_settings,
        'unit1_topics': unit1_topics,
        'unit2_topics': unit2_topics,
    }
    return render(request, 'linear_algebra/index.html', context)


def signup_view(request):
    """User Sign Up / Registration View."""
    ensure_default_data(request)
    if request.user.is_authenticated:
        return redirect('linear_algebra:dashboard')

    form = UserSignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        request.session['auth_username'] = user.username
        request.session['auth_email'] = user.email
        request.session['auth_first_name'] = user.first_name
        messages.success(request, f"Welcome to the platform, {user.first_name or user.username}! Your account has been created successfully.")
        return redirect('linear_algebra:dashboard')

    context = {
        'title': 'Create Account',
        'form': form
    }
    return render(request, 'linear_algebra/signup.html', context)


def login_view(request):
    """User Login View supporting Username or Email authentication."""
    ensure_default_data(request)
    if request.user.is_authenticated:
        return redirect('linear_algebra:dashboard')

    form = UserLoginForm(request.POST or None)
    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST' and form.is_valid():
        username_or_email = form.cleaned_data['username_or_email'].strip()
        password = form.cleaned_data['password']

        # Determine if input is email or username
        user_obj = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
            except User.DoesNotExist:
                user_obj = None
        else:
            try:
                user_obj = User.objects.get(username__iexact=username_or_email)
            except User.DoesNotExist:
                user_obj = None

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                request.session['auth_username'] = user.username
                request.session['auth_email'] = user.email
                request.session['auth_first_name'] = user.first_name
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                redirect_target = next_url if next_url and next_url.startswith('/') else 'linear_algebra:dashboard'
                return redirect(redirect_target)

        messages.error(request, "Invalid login credentials. Please check your username/email and password and try again.")

    context = {
        'title': 'Sign In',
        'form': form,
        'next': next_url
    }
    return render(request, 'linear_algebra/login.html', context)


def logout_view(request):
    """Logs out user and invalidates session."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('linear_algebra:login')


def forgot_password_view(request):
    """Password Reset Request View."""
    ensure_default_data(request)
    form = PasswordResetRequestForm(request.POST or None)
    reset_link = None

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email__iexact=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                f"/reset-password/{uid}/{token}/"
            )
            messages.success(request, f"Password reset instructions generated for {email}.")
        except User.DoesNotExist:
            messages.info(request, f"If an account exists for {email}, password reset instructions have been generated.")

    context = {
        'title': 'Forgot Password',
        'form': form,
        'reset_link': reset_link
    }
    return render(request, 'linear_algebra/forgot_password.html', context)


def reset_password_confirm_view(request, uidb64, token):
    """Set New Password Confirm View."""
    ensure_default_data(request)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        form = SetNewPasswordForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully! Please log in with your new password.")
            return redirect('linear_algebra:login')
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        form = None

    context = {
        'title': 'Set New Password',
        'form': form,
        'valid_link': user is not None and default_token_generator.check_token(user, token)
    }
    return render(request, 'linear_algebra/reset_password_confirm.html', context)


# PROTECTED VIEWS (Requires Authentication)

@login_required(login_url='linear_algebra:login')
def dashboard_view(request):
    """Authenticated Central User Dashboard."""
    site_settings = get_safe_site_settings(request)
    user_calculations = UserCalculationHistory.objects.filter(user=request.user)[:5]

    try:
        unit1_topics = list(TopicModule.objects.filter(unit='UNIT 1', is_active=True))
        unit2_topics = list(TopicModule.objects.filter(unit='UNIT 2', is_active=True))
    except Exception:
        unit1_topics = []
        unit2_topics = []

    context = {
        'title': 'User Dashboard',
        'site_settings': site_settings,
        'unit1_topics': unit1_topics,
        'unit2_topics': unit2_topics,
        'user_calculations': user_calculations,
    }
    return render(request, 'linear_algebra/dashboard.html', context)


@login_required(login_url='linear_algebra:login')
def profile_view(request):
    """User Profile and Account Settings Page."""
    ensure_default_data(request)
    profile_form = UserProfileForm(request.POST or None, instance=request.user, prefix='profile')
    password_form = UserPasswordChangeForm(request.POST or None, prefix='password')
    user_history = UserCalculationHistory.objects.filter(user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                request.session['auth_username'] = request.user.username
                request.session['auth_email'] = request.user.email
                request.session['auth_first_name'] = request.user.first_name
                messages.success(request, "Your profile information was updated successfully!")
                return redirect('linear_algebra:profile')
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                current_pw = password_form.cleaned_data['current_password']
                if not request.user.check_password(current_pw):
                    messages.error(request, "Incorrect current password. Password change aborted.")
                else:
                    new_pw = password_form.cleaned_data['new_password']
                    request.user.set_password(new_pw)
                    request.user.save()
                    # Re-authenticate session to prevent session drop
                    login(request, request.user)
                    request.session['auth_username'] = request.user.username
                    request.session['auth_email'] = request.user.email
                    request.session['auth_first_name'] = request.user.first_name
                    messages.success(request, "Your password has been updated successfully!")
                    return redirect('linear_algebra:profile')

    context = {
        'title': 'User Account & Profile Settings',
        'profile_form': profile_form,
        'password_form': password_form,
        'user_history': user_history
    }
    return render(request, 'linear_algebra/profile.html', context)


@login_required(login_url='linear_algebra:login')
def gaussian_view(request):
    """Topic 1.1: Systems of Linear Equations & Gaussian Elimination (Protected)."""
    site_settings = get_safe_site_settings(request)
    result = None
    error = None
    form = GaussianForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_gaussian_elimination(matrix_data)
            # Log calculation to user history
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='gaussian',
                topic_title='Gaussian Elimination',
                input_summary=f"Matrix: {matrix_text.replace(chr(10), ' | ')}",
                result_summary=f"Solution: {result.get('solution_summary', 'Computed')}"
            )
        except Exception as e:
            error = f"Error processing matrix input: {str(e)}"
    else:
        matrix_data = parse_matrix_input(form.fields['matrix_text'].initial)
        result = math_engine.solve_gaussian_elimination(matrix_data)

    context = {
        'title': 'Gaussian Elimination & Row Operations',
        'unit': 'Unit 1 • Topic 1',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/gaussian.html', context)


@login_required(login_url='linear_algebra:login')
def gf2_view(request):
    """Topic 1.2: Field Axioms via GF(2) (Protected)."""
    site_settings = get_safe_site_settings(request)
    result = math_engine.analyze_gf2_field()

    a_val = request.POST.get('a_val', 1) if request.method == 'POST' else 1
    b_val = request.POST.get('b_val', 1) if request.method == 'POST' else 1
    op_val = request.POST.get('op_val', 'add') if request.method == 'POST' else 'add'
    arith_result = math_engine.solve_gf2_arithmetic(a_val, b_val, op_val)

    context = {
        'title': 'Field Axioms via GF(2)',
        'unit': 'Unit 1 • Topic 2',
        'result': result,
        'arith_result': arith_result,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/gf2.html', context)


@login_required(login_url='linear_algebra:login')
def vectors_view(request):
    """Topic 1.3: 3D Vector Dot Product, Cross Product & Projections (Protected)."""
    site_settings = get_safe_site_settings(request)
    result = None
    error = None
    form = VectorsForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        v1 = [form.cleaned_data['v1_x'], form.cleaned_data['v1_y'], form.cleaned_data['v1_z']]
        v2 = [form.cleaned_data['v2_x'], form.cleaned_data['v2_y'], form.cleaned_data['v2_z']]
        try:
            result = math_engine.compute_vector_operations(v1, v2)
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='vectors',
                topic_title='Dot & Cross Product',
                input_summary=f"v1={v1}, v2={v2}",
                result_summary=f"v1.v2={result.get('dot_prod')}, Angle={result.get('angle_deg')}°"
            )
        except Exception as e:
            error = f"Error computing vector operations: {str(e)}"
    else:
        v1 = [form.fields['v1_x'].initial, form.fields['v1_y'].initial, form.fields['v1_z'].initial]
        v2 = [form.fields['v2_x'].initial, form.fields['v2_y'].initial, form.fields['v2_z'].initial]
        result = math_engine.compute_vector_operations(v1, v2)

    context = {
        'title': 'Vector Dot Product, Cross Product & Projections',
        'unit': 'Unit 1 • Topic 3',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/vectors.html', context)


@login_required(login_url='linear_algebra:login')
def gram_schmidt_view(request):
    """Topic 2.1: Gram-Schmidt Orthogonalization Process (Protected)."""
    site_settings = get_safe_site_settings(request)
    result = None
    error = None
    form = GramSchmidtForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        vectors_text = form.cleaned_data['vectors_text']
        try:
            vectors_data = parse_matrix_input(vectors_text)
            result = math_engine.solve_gram_schmidt(vectors_data)
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='gram_schmidt',
                topic_title='Gram–Schmidt Process',
                input_summary=f"Vectors: {vectors_text.replace(chr(10), ' | ')}",
                result_summary=f"Computed {len(result.get('steps', []))} orthogonal basis vectors"
            )
        except Exception as e:
            error = f"Error processing Gram-Schmidt vectors: {str(e)}"
    else:
        vectors_data = parse_matrix_input(form.fields['vectors_text'].initial)
        result = math_engine.solve_gram_schmidt(vectors_data)

    context = {
        'title': 'Gram–Schmidt Orthogonalization Process',
        'unit': 'Unit 2 • Topic 1',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/gram_schmidt.html', context)


@login_required(login_url='linear_algebra:login')
def cofactor_view(request):
    """Topic 2.2: Cofactor Expansion for Determinants (Protected)."""
    site_settings = get_safe_site_settings(request)
    result = None
    error = None
    form = CofactorForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        expand_by = form.cleaned_data['expand_by']
        idx = form.cleaned_data['index'] - 1
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_cofactor_expansion(matrix_data, expand_by, idx)
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='cofactor',
                topic_title='Cofactor Expansion',
                input_summary=f"Matrix: {matrix_text.replace(chr(10), ' | ')} (Expanded along {expand_by} {idx+1})",
                result_summary=f"det(A) = {result.get('total_det_latex')}"
            )
        except Exception as e:
            error = f"Error calculating Cofactor Expansion: {str(e)}"
    else:
        matrix_data = parse_matrix_input(form.fields['matrix_text'].initial)
        expand_by = form.fields['expand_by'].initial
        idx = form.fields['index'].initial - 1
        result = math_engine.solve_cofactor_expansion(matrix_data, expand_by, idx)

    context = {
        'title': 'Cofactor Expansion for Determinants',
        'unit': 'Unit 2 • Topic 2',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/cofactor.html', context)


@login_required(login_url='linear_algebra:login')
def diagonalization_view(request):
    """Topic 2.3: Eigenvalues, Eigenvectors & Diagonalization (Protected)."""
    site_settings = get_safe_site_settings(request)
    result = None
    error = None
    form = DiagonalizationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_diagonalization(matrix_data)
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='diagonalization',
                topic_title='Diagonalization',
                input_summary=f"Matrix: {matrix_text.replace(chr(10), ' | ')}",
                result_summary=f"Diagonalizable: {result.get('is_diagonalizable')}"
            )
        except Exception as e:
            error = f"Error in Diagonalization computation: {str(e)}"
    else:
        matrix_data = parse_matrix_input(form.fields['matrix_text'].initial)
        result = math_engine.solve_diagonalization(matrix_data)

    context = {
        'title': 'Eigenvalues, Eigenvectors & Diagonalization',
        'unit': 'Unit 2 • Topic 3',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/diagonalization.html', context)
