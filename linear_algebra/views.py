from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from .forms import (
    GaussianForm, VectorsForm, GramSchmidtForm, CofactorForm, DiagonalizationForm,
    UserSignUpForm, UserLoginForm, UserProfileForm, UserPasswordChangeForm,
    PasswordResetRequestForm, PasswordResetSetNewForm
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

def ensure_default_data():
    """Seeds SiteSetting and default TopicModules if database is empty or tables don't exist yet."""
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        print("Migrate exception in ensure_default_data:", e)

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

def get_safe_site_settings():
    """Safely retrieves SiteSetting without raising DB errors."""
    return ensure_default_data()


# ----------------------------------------------------
# PUBLIC ROUTES
# ----------------------------------------------------

def public_index_view(request):
    """Public Landing Page showing website overview, features, and authentication CTAs."""
    site_settings = get_safe_site_settings()

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
    """Public User Sign Up / Registration View."""
    ensure_default_data()
    if request.user.is_authenticated:
        return redirect('linear_algebra:dashboard')

    form = UserSignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.username = form.cleaned_data['email']
        user.set_password(form.cleaned_data['password'])
        user.save()

        login(request, user)
        messages.success(request, f"Account created successfully! Welcome to the platform, {user.first_name or user.username}.")
        return redirect('linear_algebra:dashboard')

    context = {
        'title': 'Create Your Account',
        'form': form
    }
    return render(request, 'linear_algebra/signup.html', context)


def login_view(request):
    """Public User Login View."""
    ensure_default_data()
    if request.user.is_authenticated:
        return redirect('linear_algebra:dashboard')

    form = UserLoginForm(request.POST or None)
    next_url = request.GET.get('next', 'linear_algebra:dashboard')

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['email_or_username']
        password = form.cleaned_data['password']

        user = None
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url if next_url.startswith('/') else 'linear_algebra:dashboard')
        else:
            messages.error(request, "Invalid email/username or password. Please verify your credentials and try again.")

    context = {
        'title': 'Sign In to Access Tools',
        'form': form,
        'next': next_url
    }
    return render(request, 'linear_algebra/login.html', context)


def logout_view(request):
    """User Logout View."""
    logout(request)
    messages.info(request, "You have been logged out successfully. Access to tools requires signing in.")
    return redirect('linear_algebra:index')


def forgot_password_view(request):
    """Public Forgot Password Request View."""
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email__iexact=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_url = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")
            subject = "Password Reset Instructions - Linear Algebra Explorer"
            message = f"Hello {user.first_name or user.username},\n\nYou requested a password reset for your account. Please click the link below to set a new password:\n\n{reset_url}\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nLinear Algebra Explorer Team"

            try:
                send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@linear-algebra-explorer.com'), [user.email])
            except Exception as e:
                print("Password reset email dispatch:", e)

            messages.success(request, f"Password reset instructions have been generated! Click the reset link sent to {email} or use your new password link below.")
            return render(request, 'linear_algebra/forgot_password.html', {'form': form, 'reset_demo_url': reset_url, 'success_sent': True})
        except User.DoesNotExist:
            messages.error(request, "No registered account was found with that email address. Please check your email or sign up.")

    context = {
        'title': 'Reset Your Password',
        'form': form
    }
    return render(request, 'linear_algebra/forgot_password.html', context)


def reset_password_confirm_view(request, uidb64, token):
    """Public Password Reset Confirmation View via Token."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        form = PasswordResetSetNewForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, "Your password has been reset successfully! You can now sign in with your new password.")
            return redirect('linear_algebra:login')

        context = {
            'title': 'Set New Password',
            'form': form,
            'validlink': True
        }
        return render(request, 'linear_algebra/reset_password_confirm.html', context)
    else:
        context = {
            'title': 'Invalid Reset Link',
            'validlink': False
        }
        return render(request, 'linear_algebra/reset_password_confirm.html', context)


# ----------------------------------------------------
# PROTECTED APPLICATION ROUTES (@login_required)
# ----------------------------------------------------

@login_required
def dashboard_view(request):
    """Authenticated Central User Dashboard."""
    site_settings = get_safe_site_settings()
    user_calculations = UserCalculationHistory.objects.filter(user=request.user)[:10]

    try:
        unit1_topics = list(TopicModule.objects.filter(unit='UNIT 1', is_active=True))
        unit2_topics = list(TopicModule.objects.filter(unit='UNIT 2', is_active=True))
    except Exception:
        unit1_topics = []
        unit2_topics = []

    context = {
        'title': 'User Dashboard & Tools Launcher',
        'site_settings': site_settings,
        'unit1_topics': unit1_topics,
        'unit2_topics': unit2_topics,
        'user_calculations': user_calculations,
        'total_calculations_count': UserCalculationHistory.objects.filter(user=request.user).count()
    }
    return render(request, 'linear_algebra/dashboard.html', context)


@login_required
def profile_view(request):
    """Authenticated User Profile & Account Settings."""
    profile_form = UserProfileForm(request.POST or None, instance=request.user, user=request.user)
    password_form = UserPasswordChangeForm(request.POST or None)

    if request.method == 'POST':
        if 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('linear_algebra:profile')

        elif 'change_password' in request.POST and password_form.is_valid():
            old_pass = password_form.cleaned_data['old_password']
            if request.user.check_password(old_pass):
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()
                login(request, request.user)  # Keep session active
                messages.success(request, "Your password was changed successfully!")
                return redirect('linear_algebra:profile')
            else:
                password_form.add_error('old_password', "Current password is incorrect.")

    user_history = UserCalculationHistory.objects.filter(user=request.user)

    context = {
        'title': 'User Account & Profile Settings',
        'profile_form': profile_form,
        'password_form': password_form,
        'user_history': user_history
    }
    return render(request, 'linear_algebra/profile.html', context)


@login_required
def gaussian_view(request):
    """Protected Topic 1.1: Systems of Linear Equations & Gaussian Elimination."""
    site_settings = get_safe_site_settings()
    result = None
    error = None
    form = GaussianForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_gaussian_elimination(matrix_data)

            # Record calculation in user's isolated history
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='gaussian',
                topic_title='Gaussian Elimination',
                input_summary=f"Matrix: {matrix_text.replace(chr(10), ' | ')}",
                result_summary=f"Solution: {result.get('solution_type', 'Completed')}"
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


@login_required
def gf2_view(request):
    """Protected Topic 1.2: Field Axioms via GF(2)."""
    site_settings = get_safe_site_settings()
    result = math_engine.analyze_gf2_field()

    context = {
        'title': 'Field Axioms via GF(2)',
        'unit': 'Unit 1 • Topic 2',
        'result': result,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/gf2.html', context)


@login_required
def vectors_view(request):
    """Protected Topic 1.3: 3D Vector Dot Product, Cross Product & Projections."""
    site_settings = get_safe_site_settings()
    result = None
    error = None
    form = VectorsForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        v1 = [form.cleaned_data['v1_x'], form.cleaned_data['v1_y'], form.cleaned_data['v1_z']]
        v2 = [form.cleaned_data['v2_x'], form.cleaned_data['v2_y'], form.cleaned_data['v2_z']]
        try:
            result = math_engine.compute_vector_operations(v1, v2)

            # Record calculation in user's isolated history
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='vectors',
                topic_title='Dot & Cross Product',
                input_summary=f"v1={v1}, v2={v2}",
                result_summary=f"Dot={result.get('dot_prod')}, Angle={result.get('angle_deg')}°"
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


@login_required
def gram_schmidt_view(request):
    """Protected Topic 2.1: Gram-Schmidt Orthogonalization Process."""
    site_settings = get_safe_site_settings()
    result = None
    error = None
    form = GramSchmidtForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        vectors_text = form.cleaned_data['vectors_text']
        try:
            vectors_data = parse_matrix_input(vectors_text)
            result = math_engine.solve_gram_schmidt(vectors_data)

            # Record calculation in user's isolated history
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='gram_schmidt',
                topic_title='Gram–Schmidt Process',
                input_summary=f"Vectors: {vectors_text.replace(chr(10), ' | ')}",
                result_summary=f"Calculated {len(result.get('steps', []))} orthogonal vectors"
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


@login_required
def cofactor_view(request):
    """Protected Topic 2.2: Cofactor Expansion for Determinants."""
    site_settings = get_safe_site_settings()
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

            # Record calculation in user's isolated history
            UserCalculationHistory.objects.create(
                user=request.user,
                topic_slug='cofactor',
                topic_title='Cofactor Expansion',
                input_summary=f"Matrix: {matrix_text.replace(chr(10), ' | ')} (Along {expand_by} {idx+1})",
                result_summary=f"Det = {result.get('total_det_latex')}"
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


@login_required
def diagonalization_view(request):
    """Protected Topic 2.3: Eigenvalues, Eigenvectors & Diagonalization."""
    site_settings = get_safe_site_settings()
    result = None
    error = None
    form = DiagonalizationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        matrix_text = form.cleaned_data['matrix_text']
        try:
            matrix_data = parse_matrix_input(matrix_text)
            result = math_engine.solve_diagonalization(matrix_data)

            # Record calculation in user's isolated history
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
