import inspect
from django.shortcuts import render
from .forms import GaussianForm, VectorsForm, GramSchmidtForm, CofactorForm, DiagonalizationForm
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

def index_view(request):
    """Renders main dashboard showing Unit 1 & Unit 2 topics."""
    context = {
        'title': 'Linear Algebra & Data Science Explorer',
    }
    return render(request, 'linear_algebra/index.html', context)

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
        # Default computation on initial page load
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

def gf2_view(request):
    """Topic 1.2: Field Axioms via GF(2)."""
    result = math_engine.analyze_gf2_field()
    code_snippet = inspect.getsource(math_engine.analyze_gf2_field)

    context = {
        'title': 'Field Axioms via GF(2)',
        'unit': 'Unit 1 • Topic 2',
        'result': result,
        'python_code': code_snippet
    }
    return render(request, 'linear_algebra/gf2.html', context)

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
