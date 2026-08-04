from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .forms import GaussianForm, VectorsForm, GramSchmidtForm, CofactorForm, DiagonalizationForm, SiteSettingForm, TopicModuleForm, UserRegisterForm
from .models import SiteSetting, TopicModule, SavedPreset
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
    """Seeds SiteSetting and default TopicModules if database is empty."""
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

def index_view(request):
    """Renders main dashboard pulling live settings and active topics from database."""
    site_settings = ensure_default_data()

    unit1_topics = TopicModule.objects.filter(unit='UNIT 1', is_active=True)
    unit2_topics = TopicModule.objects.filter(unit='UNIT 2', is_active=True)

    context = {
        'title': site_settings.site_title,
        'site_settings': site_settings,
        'unit1_topics': unit1_topics,
        'unit2_topics': unit2_topics,
    }
    return render(request, 'linear_algebra/index.html', context)

def register_view(request):
    """User Sign Up / Registration View."""
    if request.user.is_authenticated:
        return redirect('linear_algebra:index')

    form = UserRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome to the platform, {user.username}! Your account was created successfully.")
        return redirect('linear_algebra:index')

    context = {
        'title': 'Create Student / User Account',
        'form': form
    }
    return render(request, 'linear_algebra/register.html', context)

def login_view(request):
    """Universal Login Authentication View for all Users & Administrators."""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('linear_algebra:admin_panel')
        return redirect('linear_algebra:index')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.is_staff or user.is_superuser:
            messages.success(request, f"Welcome back, Administrator {user.username}!")
            next_url = request.GET.get('next') or 'linear_algebra:admin_panel'
        else:
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'linear_algebra:index'
        return redirect(next_url)

    context = {
        'title': 'User & Admin Sign In',
        'form': form
    }
    return render(request, 'linear_algebra/login.html', context)

def logout_view(request):
    """User Logout View."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('linear_algebra:index')

@user_passes_test(lambda u: u.is_authenticated and (u.is_staff or u.is_superuser), login_url='linear_algebra:login')
def admin_panel_view(request):
    """Custom Admin Control Panel restricted ONLY to authenticated administrators."""
    site_settings = ensure_default_data()

    topics = TopicModule.objects.all()

    if request.method == 'POST':
        if 'update_settings' in request.POST:
            setting_form = SiteSettingForm(request.POST, instance=site_settings)
            if setting_form.is_valid():
                setting_form.save()
                messages.success(request, "Website Settings updated successfully!")
                return redirect('linear_algebra:admin_panel')
        elif 'toggle_topic' in request.POST:
            topic_id = request.POST.get('topic_id')
            topic = get_object_or_404(TopicModule, id=topic_id)
            topic.is_active = not topic.is_active
            topic.save()
            status = "enabled" if topic.is_active else "disabled"
            messages.info(request, f"Topic '{topic.title}' has been {status}.")
            return redirect('linear_algebra:admin_panel')

    setting_form = SiteSettingForm(instance=site_settings)

    context = {
        'title': 'Website Control Center & Admin Panel',
        'site_settings': site_settings,
        'setting_form': setting_form,
        'topics': topics,
    }
    return render(request, 'linear_algebra/admin_panel.html', context)

def gaussian_view(request):
    """Topic 1.1: Systems of Linear Equations & Gaussian Elimination."""
    site_settings = ensure_default_data()
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

    context = {
        'title': 'Gaussian Elimination & Row Operations',
        'unit': 'Unit 1 • Topic 1',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/gaussian.html', context)

def gf2_view(request):
    """Topic 1.2: Field Axioms via GF(2)."""
    site_settings = ensure_default_data()
    result = math_engine.analyze_gf2_field()

    context = {
        'title': 'Field Axioms via GF(2)',
        'unit': 'Unit 1 • Topic 2',
        'result': result,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/gf2.html', context)

def vectors_view(request):
    """Topic 1.3: 3D Vector Dot Product, Cross Product & Projections."""
    site_settings = ensure_default_data()
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

    context = {
        'title': 'Vector Dot Product, Cross Product & Projections',
        'unit': 'Unit 1 • Topic 3',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/vectors.html', context)

def gram_schmidt_view(request):
    """Topic 2.1: Gram-Schmidt Orthogonalization Process."""
    site_settings = ensure_default_data()
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

    context = {
        'title': 'Gram–Schmidt Orthogonalization Process',
        'unit': 'Unit 2 • Topic 1',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/gram_schmidt.html', context)

def cofactor_view(request):
    """Topic 2.2: Cofactor Expansion for Determinants."""
    site_settings = ensure_default_data()
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

def diagonalization_view(request):
    """Topic 2.3: Eigenvalues, Eigenvectors & Diagonalization."""
    site_settings = ensure_default_data()
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

    context = {
        'title': 'Eigenvalues, Eigenvectors & Diagonalization',
        'unit': 'Unit 2 • Topic 3',
        'form': form,
        'result': result,
        'error': error,
        'site_settings': site_settings
    }
    return render(request, 'linear_algebra/diagonalization.html', context)
