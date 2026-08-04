"""
Linear Algebra & Data Science Math Engine
Provides step-by-step algorithms, matrix computations, LaTeX renderings, 
and proof verification for Python & Django.
"""

import numpy as np
import sympy as sp

def matrix_to_latex(matrix):
    """Converts a 2D array or SymPy Matrix to a LaTeX bmatrix string."""
    if isinstance(matrix, sp.Matrix):
        arr = matrix.tolist()
    else:
        arr = np.array(matrix).tolist()
    
    rows = []
    for row in arr:
        row_str = " & ".join([str(sp.sympify(x)) for x in row])
        rows.append(row_str)
    return r"\begin{bmatrix} " + r" \\ ".join(rows) + r" \end{bmatrix}"

def augmented_matrix_to_latex(mat, num_cols_A):
    """Formats an augmented matrix [A|b] into LaTeX pmatrix with vertical bar."""
    arr = mat.tolist() if isinstance(mat, sp.Matrix) else np.array(mat).tolist()
    col_format = "c" * num_cols_A + "|" + "c" * (len(arr[0]) - num_cols_A)
    rows = []
    for row in arr:
        row_str = " & ".join([str(sp.sympify(x)) for x in row])
        rows.append(row_str)
    return r"\left[\begin{array}{" + col_format + r"} " + r" \\ ".join(rows) + r" \end{array}\right]"

# ==========================================
# UNIT 1 - TOPIC 1: Gaussian Elimination
# ==========================================
def solve_gaussian_elimination(matrix_data):
    """
    Performs step-by-step Gaussian Elimination on an augmented matrix [A|b].
    Returns list of step dictionaries with descriptions and LaTeX matrix snapshots.
    """
    mat = sp.Matrix(matrix_data)
    rows, cols = mat.shape
    num_vars = cols - 1
    steps = []

    steps.append({
        'title': 'Initial Augmented Matrix [A | b]',
        'latex': augmented_matrix_to_latex(mat, num_vars),
        'explanation': 'The system of linear equations represented in augmented matrix form.'
    })

    current_row = 0
    mat = mat.copy()

    for c in range(num_vars):
        if current_row >= rows:
            break
        
        # Find pivot element
        pivot_row = current_row
        while pivot_row < rows and mat[pivot_row, c] == 0:
            pivot_row += 1
            
        if pivot_row == rows:
            steps.append({
                'title': f'Column {c+1} has no non-zero pivot',
                'latex': augmented_matrix_to_latex(mat, num_vars),
                'explanation': f'No non-zero pivot found in column {c+1}. Moving to next column.'
            })
            continue

        # Swap rows if necessary
        if pivot_row != current_row:
            mat.row_swap(current_row, pivot_row)
            steps.append({
                'title': f'Row Swap: R_{{{current_row+1}}} \\leftrightarrow R_{{{pivot_row+1}}}',
                'latex': augmented_matrix_to_latex(mat, num_vars),
                'explanation': f'Swapped Row {current_row+1} with Row {pivot_row+1} to bring non-zero pivot {mat[current_row, c]} to position ({current_row+1}, {c+1}).'
            })

        pivot_val = mat[current_row, c]
        
        # Scale row to make pivot equal to 1
        if pivot_val != 1 and pivot_val != 0:
            mat.row_op(current_row, lambda val, j: val / pivot_val)
            steps.append({
                'title': f'Scale Pivot Row: R_{{{current_row+1}}} \\leftarrow \\frac{{1}}{{{sp.latex(pivot_val)}}} R_{{{current_row+1}}}',
                'latex': augmented_matrix_to_latex(mat, num_vars),
                'explanation': f'Divided Row {current_row+1} by its pivot value {pivot_val} to make leading entry 1.'
            })

        # Eliminate entries below and above (RREF)
        for r in range(rows):
            if r != current_row and mat[r, c] != 0:
                factor = mat[r, c]
                mat.row_op(r, lambda val, j: val - factor * mat[current_row, j])
                steps.append({
                    'title': f'Row Elimination: R_{{{r+1}}} \\leftarrow R_{{{r+1}}} - ({sp.latex(factor)}) R_{{{current_row+1}}}',
                    'latex': augmented_matrix_to_latex(mat, num_vars),
                    'explanation': f'Eliminated entry in Row {r+1}, Column {c+1} using Row {current_row+1}.'
                })

        current_row += 1

    # Classify solution type
    rref_mat, pivot_cols = mat.rref()
    A_part = mat[:, :num_vars]
    b_part = mat[:, num_vars]
    
    rank_A = A_part.rank()
    rank_aug = mat.rank()
    
    solution_summary = ""
    solution_latex = ""

    if rank_A < rank_aug:
        solution_type = "Inconsistent System (No Solution)"
        solution_summary = "The rank of coefficient matrix A is strictly less than the rank of augmented matrix [A|b]. A row reduced to [0 0 ... 0 | c] where c ≠ 0."
        solution_latex = r"\text{No Solution } (\emptyset)"
    elif rank_A == rank_aug == num_vars:
        solution_type = "Unique Solution"
        solutions = []
        for i in range(num_vars):
            solutions.append(rf"x_{{{i+1}}} = {sp.latex(mat[i, num_vars])}")
        solution_latex = ", \\quad ".join(solutions)
        solution_summary = "The system has exactly one unique solution vector."
    else:
        solution_type = "Infinitely Many Solutions (Parametric)"
        solution_summary = f"Rank = {rank_A} < {num_vars} variables. The system has {num_vars - rank_A} free variable(s)."
        sol_dict = sp.solve_linear_system(mat, *[sp.Symbol(f'x_{i+1}') for i in range(num_vars)])
        solution_latex = r"\begin{cases} " + r" \\ ".join([f"{sp.latex(k)} = {sp.latex(v)}" for k, v in sol_dict.items()]) + r" \end{cases}"

    return {
        'steps': steps,
        'final_latex': augmented_matrix_to_latex(mat, num_vars),
        'solution_type': solution_type,
        'solution_summary': solution_summary,
        'solution_latex': solution_latex
    }

# ==========================================
# UNIT 1 - TOPIC 2: Field Axioms via GF(2)
# ==========================================
def analyze_gf2_field():
    """
    Generates GF(2) Galois Field addition/multiplication tables 
    and checks all 11 field axioms explicitly.
    """
    elements = [0, 1]
    
    # Addition table (XOR / mod 2)
    add_table = [[(a + b) % 2 for b in elements] for a in elements]
    
    # Multiplication table (AND / mod 2)
    mul_table = [[(a * b) % 2 for b in elements] for a in elements]

    axioms = []

    # 1. Addition Closure
    add_closed = all((a + b) % 2 in elements for a in elements for b in elements)
    axioms.append({
        'name': 'Additive Closure',
        'symbol': r'\forall a, b \in \mathbb{F}_2, \; a + b \in \mathbb{F}_2',
        'passed': add_closed,
        'proof': '0+0=0, 0+1=1, 1+0=1, 1+1=0. All results belong to {0, 1}.'
    })

    # 2. Addition Associativity
    add_assoc = all(((a + b) + c) % 2 == (a + (b + c)) % 2 for a in elements for b in elements for c in elements)
    axioms.append({
        'name': 'Additive Associativity',
        'symbol': r'(a + b) + c = a + (b + c)',
        'passed': add_assoc,
        'proof': 'Verified for all 2³ = 8 combinations of (a, b, c) in GF(2).'
    })

    # 3. Addition Commutativity
    add_comm = all((a + b) % 2 == (b + a) % 2 for a in elements for b in elements)
    axioms.append({
        'name': 'Additive Commutativity',
        'symbol': r'a + b = b + a',
        'passed': add_comm,
        'proof': 'Addition table is symmetric across its main diagonal.'
    })

    # 4. Additive Identity (0)
    add_id = 0
    has_add_id = all((a + add_id) % 2 == a for a in elements)
    axioms.append({
        'name': 'Additive Identity',
        'symbol': r'\exists 0 \in \mathbb{F}_2 \; \text{s.t.} \; a + 0 = a',
        'passed': has_add_id,
        'proof': '0 acts as identity element: 0+0=0, 1+0=1.'
    })

    # 5. Additive Inverses
    add_inv = {a: [b for b in elements if (a + b) % 2 == 0][0] for a in elements}
    axioms.append({
        'name': 'Additive Inverse',
        'symbol': r'\forall a \in \mathbb{F}_2, \; \exists (-a) \text{ s.t. } a + (-a) = 0',
        'passed': True,
        'proof': 'In GF(2), every element is its own additive inverse: -0 = 0 (0+0=0) and -1 = 1 (1+1=0).'
    })

    # 6. Multiplication Closure
    mul_closed = all((a * b) % 2 in elements for a in elements for b in elements)
    axioms.append({
        'name': 'Multiplicative Closure',
        'symbol': r'\forall a, b \in \mathbb{F}_2, \; a \cdot b \in \mathbb{F}_2',
        'passed': mul_closed,
        'proof': '0·0=0, 0·1=0, 1·0=0, 1·1=1. All results belong to {0, 1}.'
    })

    # 7. Multiplication Associativity
    mul_assoc = all(((a * b) * c) % 2 == (a * (b * c)) % 2 for a in elements for b in elements for c in elements)
    axioms.append({
        'name': 'Multiplicative Associativity',
        'symbol': r'(a \cdot b) \cdot c = a \cdot (b \cdot c)',
        'passed': mul_assoc,
        'proof': 'Verified for all 8 combinations of (a, b, c).'
    })

    # 8. Multiplication Commutativity
    mul_comm = all((a * b) % 2 == (b * a) % 2 for a in elements for b in elements)
    axioms.append({
        'name': 'Multiplicative Commutativity',
        'symbol': r'a \cdot b = b \cdot a',
        'passed': mul_comm,
        'proof': 'Multiplication table is symmetric.'
    })

    # 9. Multiplicative Identity (1)
    mul_id = 1
    has_mul_id = all((a * mul_id) % 2 == a for a in elements)
    axioms.append({
        'name': 'Multiplicative Identity',
        'symbol': r'\exists 1 \in \mathbb{F}_2 \; \text{s.t.} \; a \cdot 1 = a',
        'passed': has_mul_id,
        'proof': '1 acts as multiplicative identity element: 0·1=0, 1·1=1.'
    })

    # 10. Multiplicative Inverse for non-zero elements
    axioms.append({
        'name': 'Multiplicative Inverse (Non-Zero)',
        'symbol': r'\forall a \neq 0, \; \exists a^{-1} \text{ s.t. } a \cdot a^{-1} = 1',
        'passed': True,
        'proof': 'The non-zero element 1 has inverse 1⁻¹ = 1 because 1 · 1 = 1 (mod 2).'
    })

    # 11. Distributivity
    distrib = all((a * ((b + c) % 2)) % 2 == ((a * b) + (a * c)) % 2 for a in elements for b in elements for c in elements)
    axioms.append({
        'name': 'Distributive Law',
        'symbol': r'a \cdot (b + c) = (a \cdot b) + (a \cdot c)',
        'passed': distrib,
        'proof': 'Multiplication distributes over addition for all 8 combinations in GF(2).'
    })

    return {
        'elements': elements,
        'add_table': add_table,
        'mul_table': mul_table,
        'axioms': axioms,
        'is_field': all(ax['passed'] for ax in axioms)
    }

def solve_gf2_arithmetic(a_val, b_val, op='add'):
    """
    Computes step-by-step modular binary arithmetic in GF(2) = {0, 1}.
    """
    a = int(a_val) % 2
    b = int(b_val) % 2
    
    if op == 'add':
        res = (a + b) % 2
        formula_latex = rf"{a} \oplus {b} = ({a} + {b}) \pmod{{2}} = {res}"
        explanation = f"In GF(2), addition is equivalent to bitwise XOR: {a} + {b} = {a+b}, and ({a+b}) mod 2 = {res}."
    elif op == 'mul':
        res = (a * b) % 2
        formula_latex = rf"{a} \odot {b} = ({a} \cdot {b}) \pmod{{2}} = {res}"
        explanation = f"In GF(2), multiplication is equivalent to bitwise AND: {a} · {b} = {a*b}, and ({a*b}) mod 2 = {res}."
    else:
        res = (a + b) % 2
        formula_latex = rf"{a} + {b} \equiv {res} \pmod{{2}}"
        explanation = "GF(2) binary arithmetic step."

    return {
        'a': a,
        'b': b,
        'op': op,
        'res': res,
        'formula_latex': formula_latex,
        'explanation': explanation
    }

# ==========================================
# UNIT 1 - TOPIC 3: Vectors (Dot & Cross Product)
# ==========================================
def compute_vector_operations(v1_list, v2_list):
    """
    Computes 3D Vector operations: Dot product, Cross product, Angles, Projections.
    Returns explicit step-by-step LaTeX derivations for display.
    """
    v1 = np.array(v1_list, dtype=float)
    v2 = np.array(v2_list, dtype=float)

    mag1 = np.linalg.norm(v1)
    mag2 = np.linalg.norm(v2)

    dot_prod = np.dot(v1, v2)
    cross_prod = np.cross(v1, v2)
    cross_mag = np.linalg.norm(cross_prod)

    # Step-by-step LaTeX strings
    step_dot_latex = rf"\mathbf{{u}} \cdot \mathbf{{v}} = ({v1[0]} \cdot {v2[0]}) + ({v1[1]} \cdot {v2[1]}) + ({v1[2]} \cdot {v2[2]}) = {v1[0]*v2[0]} + {v1[1]*v2[1]} + {v1[2]*v2[2]} = {round(float(dot_prod), 4)}"
    
    step_mag1_latex = rf"\|\mathbf{{u}}\| = \sqrt{{({v1[0]})^2 + ({v1[1]})^2 + ({v1[2]})^2}} = \sqrt{{{round(float(v1[0]**2 + v1[1]**2 + v1[2]**2), 4)}}} = {round(float(mag1), 4)}"
    step_mag2_latex = rf"\|\mathbf{{v}}\| = \sqrt{{({v2[0]})^2 + ({v2[1]})^2 + ({v2[2]})^2}} = \sqrt{{{round(float(v2[0]**2 + v2[1]**2 + v2[2]**2), 4)}}} = {round(float(mag2), 4)}"

    # Cross product 3x3 expansion
    c_i = v1[1]*v2[2] - v1[2]*v2[1]
    c_j = v1[2]*v2[0] - v1[0]*v2[2]
    c_k = v1[0]*v2[1] - v1[1]*v2[0]
    step_cross_latex = (
        r"\mathbf{u} \times \mathbf{v} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ "
        + f"{v1[0]} & {v1[1]} & {v1[2]} \\ {v2[0]} & {v2[1]} & {v2[2]}"
        + r" \end{vmatrix} = \left( (" + f"{v1[1]}" + r")\cdot(" + f"{v2[2]}" + r") - (" + f"{v1[2]}" + r")\cdot(" + f"{v2[1]}" + r") \right)\mathbf{i} - \left( (" + f"{v1[0]}" + r")\cdot(" + f"{v2[2]}" + r") - (" + f"{v1[2]}" + r")\cdot(" + f"{v2[0]}" + r") \right)\mathbf{j} + \left( (" + f"{v1[0]}" + r")\cdot(" + f"{v2[1]}" + r") - (" + f"{v1[1]}" + r")\cdot(" + f"{v2[0]}" + r") \right)\mathbf{k} = "
        + f"{round(c_i, 4)}" + r"\mathbf{i} + (" + f"{round(c_j, 4)}" + r")\mathbf{j} + (" + f"{round(c_k, 4)}" + r")\mathbf{k}"
    )

    # Angle calculation
    if mag1 > 0 and mag2 > 0:
        cos_theta = np.clip(dot_prod / (mag1 * mag2), -1.0, 1.0)
        angle_rad = np.arccos(cos_theta)
        angle_deg = np.degrees(angle_rad)
        step_angle_latex = rf"\cos(\theta) = \frac{{\mathbf{{u}} \cdot \mathbf{{v}}}}{{\|\mathbf{{u}}\| \|\mathbf{{v}}\|}} = \frac{{{round(float(dot_prod), 4)}}}{{{round(float(mag1), 4)} \cdot {round(float(mag2), 4)}}} = {round(float(cos_theta), 4)} \implies \theta = {round(float(angle_deg), 2)}^\circ"
    else:
        cos_theta, angle_rad, angle_deg = 0.0, 0.0, 0.0
        step_angle_latex = r"\theta = \text{Undefined (zero vector)}"

    is_orthogonal = np.isclose(dot_prod, 0.0)
    is_parallel = np.isclose(cross_mag, 0.0)

    # Vector projection proj_v2(v1)
    if mag2 > 0:
        proj_scalar = dot_prod / (mag2 ** 2)
        proj_vector = proj_scalar * v2
        step_proj_latex = (
            r"\text{proj}_{\mathbf{v}}(\mathbf{u}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{v}\|^2} \mathbf{v} = \frac{"
            + f"{round(float(dot_prod), 4)}" + r"}{" + f"{round(float(mag2**2), 4)}" + r"} \begin{bmatrix} "
            + f"{v2[0]} \\ {v2[1]} \\ {v2[2]}" + r" \end{bmatrix} = \begin{bmatrix} "
            + f"{round(float(proj_vector[0]), 4)} \\ {round(float(proj_vector[1]), 4)} \\ {round(float(proj_vector[2]), 4)}" + r" \end{bmatrix}"
        )
    else:
        proj_scalar = 0.0
        proj_vector = np.array([0.0, 0.0, 0.0])
        step_proj_latex = r"\text{proj}_{\mathbf{v}}(\mathbf{u}) = \mathbf{0}"

    unit_v1 = (v1 / mag1) if mag1 > 0 else np.array([0.0, 0.0, 0.0])
    unit_v2 = (v2 / mag2) if mag2 > 0 else np.array([0.0, 0.0, 0.0])

    return {
        'v1': v1.tolist(),
        'v2': v2.tolist(),
        'mag1': round(float(mag1), 4),
        'mag2': round(float(mag2), 4),
        'unit_v1': np.round(unit_v1, 4).tolist(),
        'unit_v2': np.round(unit_v2, 4).tolist(),
        'dot_prod': round(float(dot_prod), 4),
        'cross_prod': np.round(cross_prod, 4).tolist(),
        'cross_mag': round(float(cross_mag), 4),
        'angle_rad': round(float(angle_rad), 4),
        'angle_deg': round(float(angle_deg), 2),
        'proj_vector': np.round(proj_vector, 4).tolist(),
        'proj_scalar': round(float(proj_scalar), 4),
        'is_orthogonal': bool(is_orthogonal),
        'is_parallel': bool(is_parallel),
        'triangle_area': round(float(cross_mag / 2.0), 4),
        'parallelepiped_area': round(float(cross_mag), 4),
        'step_dot_latex': step_dot_latex,
        'step_mag1_latex': step_mag1_latex,
        'step_mag2_latex': step_mag2_latex,
        'step_cross_latex': step_cross_latex,
        'step_angle_latex': step_angle_latex,
        'step_proj_latex': step_proj_latex,
    }

# ==========================================
# UNIT 2 - TOPIC 1: Gram-Schmidt Process
# ==========================================
def solve_gram_schmidt(vectors_data):
    """
    Applies the Gram-Schmidt orthogonalization process to a set of input vectors.
    """
    orig_vectors = [sp.Matrix(v) for v in vectors_data]
    k = len(orig_vectors)
    u_vectors = []  # Orthogonal vectors
    e_vectors = []  # Orthonormal vectors
    steps = []

    for i in range(k):
        v_i = orig_vectors[i]
        proj_terms = []
        proj_latex_list = []
        
        u_i = v_i.copy()
        
        for j in range(i):
            u_j = u_vectors[j]
            dot_v_u = v_i.dot(u_j)
            dot_u_u = u_j.dot(u_j)
            proj_coeff = dot_v_u / dot_u_u
            proj_vec = proj_coeff * u_j
            u_i = u_i - proj_vec
            
            proj_latex_list.append(
                rf"\text{{proj}}_{{\mathbf{{u}}_{{{j+1}}}}}(\mathbf{{v}}_{{{i+1}}}) = \frac{{\mathbf{{v}}_{{{i+1}}} \cdot \mathbf{{u}}_{{{j+1}}}}}{{\|\mathbf{{u}}_{{{j+1}}}\|^2}} \mathbf{{u}}_{{{j+1}}} = \frac{{{sp.latex(dot_v_u)}}}{{{sp.latex(dot_u_u)}}} {matrix_to_latex(u_j)} = {matrix_to_latex(proj_vec)}"
            )

        u_vectors.append(u_i)
        u_norm = sp.sqrt(u_i.dot(u_i))
        e_i = u_i / u_norm if u_norm != 0 else u_i
        e_vectors.append(e_i)

        steps.append({
            'step_num': i + 1,
            'v_latex': matrix_to_latex(v_i),
            'proj_explanations': proj_latex_list,
            'u_latex': matrix_to_latex(u_i),
            'u_norm_latex': sp.latex(u_norm),
            'e_latex': matrix_to_latex(e_i)
        })

    # Inner product verification matrix (Orthogonality check)
    ortho_matrix = []
    for i in range(k):
        row = []
        for j in range(k):
            val = e_vectors[i].dot(e_vectors[j])
            row.append(sp.simplify(val))
        ortho_matrix.append(row)

    return {
        'steps': steps,
        'orthogonal_basis': [matrix_to_latex(u) for u in u_vectors],
        'orthonormal_basis': [matrix_to_latex(e) for e in e_vectors],
        'ortho_check_latex': matrix_to_latex(sp.Matrix(ortho_matrix))
    }

# ==========================================
# UNIT 2 - TOPIC 2: Cofactor Expansion
# ==========================================
def solve_cofactor_expansion(matrix_data, expand_by='row', idx=0):
    """
    Computes determinant of square matrix using Cofactor Expansion 
    along a specific row or column (0-indexed).
    """
    mat = sp.Matrix(matrix_data)
    n, m = mat.shape
    if n != m:
        raise ValueError("Matrix must be square for Cofactor Expansion.")

    terms = []
    total_det = 0

    if expand_by == 'row':
        r = idx
        for c in range(n):
            val = mat[r, c]
            sub_mat = mat.minor_submatrix(r, c)
            sign = (-1) ** (r + c)
            minor_det = sub_mat.det()
            cofactor = sign * minor_det
            term_val = val * cofactor
            total_det += term_val

            terms.append({
                'row': r + 1,
                'col': c + 1,
                'entry': sp.latex(val),
                'sign': f"(-1)^{{{r+1}+{c+1}}} = {sign}",
                'submatrix_latex': matrix_to_latex(sub_mat),
                'minor_det_latex': sp.latex(minor_det),
                'cofactor_latex': sp.latex(cofactor),
                'term_latex': rf"({sp.latex(val)}) \cdot ({sp.latex(cofactor)}) = {sp.latex(term_val)}"
            })
    else:
        c = idx
        for r in range(n):
            val = mat[r, c]
            sub_mat = mat.minor_submatrix(r, c)
            sign = (-1) ** (r + c)
            minor_det = sub_mat.det()
            cofactor = sign * minor_det
            term_val = val * cofactor
            total_det += term_val

            terms.append({
                'row': r + 1,
                'col': c + 1,
                'entry': sp.latex(val),
                'sign': f"(-1)^{{{r+1}+{c+1}}} = {sign}",
                'submatrix_latex': matrix_to_latex(sub_mat),
                'minor_det_latex': sp.latex(minor_det),
                'cofactor_latex': sp.latex(cofactor),
                'term_latex': rf"({sp.latex(val)}) \cdot ({sp.latex(cofactor)}) = {sp.latex(term_val)}"
            })

    # Checkerboard sign matrix
    sign_matrix = [[f"+1" if (i+j)%2==0 else "-1" for j in range(n)] for i in range(n)]

    return {
        'matrix_latex': matrix_to_latex(mat),
        'expand_by': expand_by,
        'index': idx + 1,
        'terms': terms,
        'total_det_latex': sp.latex(total_det),
        'sign_matrix_latex': matrix_to_latex(sp.Matrix(sign_matrix))
    }

# ==========================================
# UNIT 2 - TOPIC 3: Eigenvalues, Eigenvectors & Diagonalization
# ==========================================
def solve_diagonalization(matrix_data):
    """
    Calculates Characteristic Polynomial, Eigenvalues, Eigenvectors, 
    and checks Diagonalization A = P D P^-1.
    """
    mat = sp.Matrix(matrix_data)
    n, m = mat.shape
    if n != m:
        raise ValueError("Matrix must be square for Diagonalization.")

    lam = sp.Symbol('\\lambda')
    char_poly_mat = mat - lam * sp.eye(n)
    char_poly = char_poly_mat.det()
    
    # Eigenvalues and multiplicities
    eigen_info = mat.eigenvects()
    
    eigenvalues_summary = []
    P_cols = []
    D_diag = []

    is_diagonalizable = True
    total_geometric_mult = 0

    for item in eigen_info:
        val, alg_mult, vects = item
        geom_mult = len(vects)
        total_geometric_mult += geom_mult

        vects_latex = [matrix_to_latex(v) for v in vects]
        
        for v in vects:
            P_cols.append(v)
            D_diag.append(val)

        eigenvalues_summary.append({
            'eigenvalue_latex': sp.latex(val),
            'alg_mult': alg_mult,
            'geom_mult': geom_mult,
            'eigenvectors_latex': vects_latex
        })

    if total_geometric_mult < n:
        is_diagonalizable = False

    if is_diagonalizable:
        P_mat = sp.Matrix.hstack(*P_cols)
        D_mat = sp.diag(*D_diag)
        P_inv = P_mat.inv()
        verification_mat = P_mat * D_mat * P_inv
    else:
        P_mat = None
        D_mat = None
        P_inv = None
        verification_mat = None

    return {
        'matrix_latex': matrix_to_latex(mat),
        'char_poly_latex': sp.latex(sp.expand(char_poly)),
        'eigenvalues_summary': eigenvalues_summary,
        'is_diagonalizable': is_diagonalizable,
        'P_latex': matrix_to_latex(P_mat) if P_mat else r"\text{N/A}",
        'D_latex': matrix_to_latex(D_mat) if D_mat else r"\text{N/A}",
        'P_inv_latex': matrix_to_latex(P_inv) if P_inv else r"\text{N/A}",
        'verification_latex': matrix_to_latex(verification_mat) if verification_mat else r"\text{N/A}"
    }
