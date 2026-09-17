"""
Linear Algebra & Data Science Math Engine
Provides step-by-step algorithms, matrix computations, LaTeX renderings, 
and proof verification for Python & Django.
All decimal values across all solvers are cleanly formatted to at most 2 decimal places.
"""

import math
import random
import re
import numpy as np
import sympy as sp
from sympy import factorint, gcdex
import plotly.graph_objects as go

def clean_val_2dp(x):
    """
    Cleanly formats numbers into integers or clean decimals with at most 2 decimal places.
    Converts SymPy Floats 1.00000000000000 -> 1, 3.14159265 -> 3.14, -11.00000 -> -11.
    """
    try:
        val = sp.sympify(x)
        if isinstance(val, (sp.Float, float)):
            fval = float(val)
            if fval.is_integer():
                return sp.Integer(int(fval))
            return sp.Float(round(fval, 2))
        elif isinstance(val, sp.Basic):
            floats = val.atoms(sp.Float)
            replaces = {}
            for fl in floats:
                fval = float(fl)
                if fval.is_integer():
                    replaces[fl] = sp.Integer(int(fval))
                else:
                    replaces[fl] = sp.Float(round(fval, 2))
            if replaces:
                val = val.subs(replaces)
            return val
        return val
    except Exception:
        return x

def clean_val_str(x):
    """Converts a value to clean string representation with max 2 decimal places."""
    cleaned = clean_val_2dp(x)
    if isinstance(cleaned, sp.Float):
        fval = float(cleaned)
        if fval.is_integer():
            return str(int(fval))
        return f"{fval:.2f}".rstrip('0').rstrip('.')
    return str(sp.sympify(cleaned))

def matrix_to_latex(matrix):
    """Converts a 2D array or SymPy Matrix to a LaTeX bmatrix string with max 2 decimal places."""
    if matrix is None:
        return r"\text{N/A}"
    if isinstance(matrix, sp.Matrix):
        arr = matrix.tolist()
    else:
        arr = np.array(matrix).tolist()
    
    rows = []
    for row in arr:
        row_str = " & ".join([sp.latex(clean_val_2dp(x)) for x in row])
        rows.append(row_str)
    return r"\begin{bmatrix} " + r" \\ ".join(rows) + r" \end{bmatrix}"

def augmented_matrix_to_latex(mat, num_cols_A):
    """Formats an augmented matrix [A|b] into LaTeX pmatrix with vertical bar with max 2 decimal places."""
    if mat is None:
        return r"\text{N/A}"
    arr = mat.tolist() if isinstance(mat, sp.Matrix) else np.array(mat).tolist()
    col_format = "c" * num_cols_A + "|" + "c" * (len(arr[0]) - num_cols_A)
    rows = []
    for row in arr:
        row_str = " & ".join([sp.latex(clean_val_2dp(x)) for x in row])
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
        'title': r'Initial Augmented Matrix $[A \mid b]$',
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
                'title': f'Column {c+1} Has No Non-Zero Pivot',
                'latex': augmented_matrix_to_latex(mat, num_vars),
                'explanation': f'No non-zero pivot found in column {c+1}. Moving to next column.'
            })
            continue

        # Swap rows if necessary
        if pivot_row != current_row:
            mat.row_swap(current_row, pivot_row)
            steps.append({
                'title': f'Row Swap: $R_{{{current_row+1}}} \\leftrightarrow R_{{{pivot_row+1}}}$',
                'latex': augmented_matrix_to_latex(mat, num_vars),
                'explanation': f'Swapped Row {current_row+1} with Row {pivot_row+1} to bring non-zero pivot {clean_val_str(mat[current_row, c])} to position ({current_row+1}, {c+1}).'
            })

        pivot_val = mat[current_row, c]
        
        # Scale row to make pivot equal to 1
        if pivot_val != 1 and pivot_val != 0:
            mat.row_op(current_row, lambda val, j: val / pivot_val)
            steps.append({
                'title': f'Scale Pivot Row: $R_{{{current_row+1}}} \\leftarrow \\frac{{1}}{{{sp.latex(clean_val_2dp(pivot_val))}}} R_{{{current_row+1}}}$',
                'latex': augmented_matrix_to_latex(mat, num_vars),
                'explanation': f'Divided Row {current_row+1} by its pivot value {clean_val_str(pivot_val)} to make leading entry 1.'
            })

        # Eliminate entries below and above (RREF)
        for r in range(rows):
            if r != current_row and mat[r, c] != 0:
                factor = mat[r, c]
                mat.row_op(r, lambda val, j: val - factor * mat[current_row, j])
                steps.append({
                    'title': f'Row Elimination: $R_{{{r+1}}} \\leftarrow R_{{{r+1}}} - ({sp.latex(clean_val_2dp(factor))}) R_{{{current_row+1}}}$',
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
            solutions.append(rf"x_{{{i+1}}} = {sp.latex(clean_val_2dp(mat[i, num_vars]))}")
        solution_latex = ", \\quad ".join(solutions)
        solution_summary = "The system has exactly one unique solution vector."
    else:
        solution_type = "Infinitely Many Solutions (Parametric)"
        solution_summary = f"Rank = {rank_A} < {num_vars} variables. The system has {num_vars - rank_A} free variable(s)."
        sol_dict = sp.solve_linear_system(mat, *[sp.Symbol(f'x_{i+1}') for i in range(num_vars)])
        solution_latex = r"\begin{cases} " + r" \\ ".join([f"{sp.latex(k)} = {sp.latex(clean_val_2dp(v))}" for k, v in sol_dict.items()]) + r" \end{cases}"

    return {
        'steps': steps,
        'final_latex': augmented_matrix_to_latex(mat, num_vars),
        'solution_type': solution_type,
        'solution_summary': solution_summary,
        'solution_latex': solution_latex
    }

# ==========================================
# UNIT 1 - TOPIC 2: Galois / Finite Field Engine
# ==========================================

def is_prime_number(n):

    """Returns True if n is a prime number, False otherwise."""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def compute_gf2_calc(a, b, op, modulus=2):
    """Calculates custom binary/modular addition or multiplication in F_p."""
    mod = max(2, int(modulus))
    a_val = int(a) % mod
    b_val = int(b) % mod
    if op == 'add':
        res = (a_val + b_val) % mod
        latex = f"{a_val} + {b_val} = {res} \\pmod{{{mod}}}"
        explanation = f"Modular Addition in F_{mod}: ({a_val} + {b_val}) mod {mod} = {res}"
    else:
        res = (a_val * b_val) % mod
        latex = f"{a_val} \\cdot {b_val} = {res} \\pmod{{{mod}}}"
        explanation = f"Modular Multiplication in F_{mod}: ({a_val} · {b_val}) mod {mod} = {res}"
    return {
        'a': a_val,
        'b': b_val,
        'op': op,
        'modulus': mod,
        'result': res,
        'latex': latex,
        'explanation': explanation
    }

def analyze_gf2_field():
    """Returns field analysis for GF(2)."""
    return analyze_galois_field(modulus=2)

def analyze_galois_field(modulus=2, task='verify_field_axioms', custom_question=None):


    """
    Generates Galois / Finite Field F_p addition and multiplication tables dynamically,
    evaluates all 11 field axioms, calculates additive/multiplicative inverses,
    and returns comprehensive proof & step-by-step verification.
    """
    p = max(2, int(modulus))
    elements = list(range(p))
    elems_str = ", ".join(map(str, elements))
    is_field = is_prime_number(p)
    
    subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    field_subscript = str(p).translate(subscript_map)
    field_notation = f"F{field_subscript}"
    latex_field = f"\\mathbb{{F}}_{{{p}}}"

    # Generate Addition & Multiplication Tables dynamically
    add_table = [[(a + b) % p for b in elements] for a in elements]
    mul_table = [[(a * b) % p for b in elements] for a in elements]

    # Generate Additive Inverses
    add_inverses = {}
    add_inverses_latex = []
    for a in elements:
        inv = (p - a) % p
        add_inverses[a] = inv
        add_inverses_latex.append(f"-{a} \\equiv {inv} \\pmod{{{p}}}")

    # Generate Multiplicative Inverses
    mul_inverses = {}
    mul_inverses_latex = []
    zero_divisors = []
    
    for a in elements:
        if a == 0:
            mul_inverses[0] = None
            continue
        inv = None
        for b in range(1, p):
            if (a * b) % p == 1:
                inv = b
                break
        mul_inverses[a] = inv
        if inv is not None:
            mul_inverses_latex.append(f"{a}^{{-1}} \\equiv {inv} \\pmod{{{p}}}")
        else:
            zero_divisors.append(a)
            mul_inverses_latex.append(f"{a}^{{-1}} \\text{{ does not exist in }} \\mathbb{{Z}}_{{{p}}}")

    # Explicit 11 Field Axiom Evaluation
    axioms = []

    # 1. Addition Closure
    add_closed = all((a + b) % p in elements for a in elements for b in elements)
    axioms.append({
        'name': 'Additive Closure',
        'symbol': f'\\forall a, b \\in {latex_field}, \\; a + b \\in {latex_field}',
        'passed': add_closed,
        'check_needed': f'Verify that for all $a, b \\in \\{{' + elems_str + f'\\}}$, $(a + b) \\bmod {p} \\in {latex_field}$.',
        'proof': f'Sum of any two elements modulo {p} always stays in the set $\\{{' + elems_str + f'\\}}.$'
    })

    # 2. Addition Associativity
    add_assoc = all(((a + b) + c) % p == (a + (b + c)) % p for a in elements for b in elements for c in elements)
    axioms.append({
        'name': 'Additive Associativity',
        'symbol': r'(a + b) + c = a + (b + c)',
        'passed': add_assoc,
        'check_needed': f'Verify $(a + b) + c \\equiv a + (b + c) \\pmod{{{p}}}$ for all $p^3 = {p**3}$ triplets.',
        'proof': f'Modular addition is associative across all {p**3} element combinations in {field_notation}.'
    })

    # 3. Addition Commutativity
    add_comm = all((a + b) % p == (b + a) % p for a in elements for b in elements)
    axioms.append({
        'name': 'Additive Commutativity',
        'symbol': r'a + b = b + a',
        'passed': add_comm,
        'check_needed': f'Verify $a + b \\equiv b + a \\pmod{{{p}}}$ for all elements.',
        'proof': f'The addition table for {field_notation} is completely symmetric across its main diagonal.'
    })

    # 4. Additive Identity (0)
    has_add_id = all((a + 0) % p == a for a in elements)
    axioms.append({
        'name': 'Additive Identity',
        'symbol': f'\\exists 0 \\in {latex_field} \\; \\text{{s.t.}} \\; a + 0 = a',
        'passed': has_add_id,
        'check_needed': f'Check if element $0$ satisfies $a + 0 \\equiv a \\pmod{{{p}}}$ for all $a$.',
        'proof': f'0 acts as the unique additive identity element in {field_notation}.'
    })

    # 5. Additive Inverses
    has_add_inv = all(add_inverses[a] is not None for a in elements)
    inv_examples = ", ".join([f"-{a} = {add_inverses[a]}" for a in elements[:4]])
    axioms.append({
        'name': 'Additive Inverse',
        'symbol': f'\\forall a \\in {latex_field}, \\exists (-a) \\text{{ s.t. }} a + (-a) = 0',
        'passed': has_add_inv,
        'check_needed': f'Check if every $a \\in {field_notation}$ has $-a \\equiv (({p}-a) \\bmod {p})$.',
        'proof': f'Every element has a unique additive inverse: {inv_examples}.'
    })

    # 6. Multiplication Closure
    mul_closed = all((a * b) % p in elements for a in elements for b in elements)
    axioms.append({
        'name': 'Multiplicative Closure',
        'symbol': f'\\forall a, b \\in {latex_field}, \\; a \\cdot b \\in {latex_field}',
        'passed': mul_closed,
        'check_needed': f'Verify that $(a \\cdot b) \\bmod {p} \\in {latex_field}$ for all $a, b$.',
        'proof': f'Product of any two elements modulo {p} belongs to $\\{{' + elems_str + f'\\}}.$'
    })

    # 7. Multiplication Associativity
    mul_assoc = all(((a * b) * c) % p == (a * (b * c)) % p for a in elements for b in elements for c in elements)
    axioms.append({
        'name': 'Multiplicative Associativity',
        'symbol': r'(a \cdot b) \cdot c = a \cdot (b \cdot c)',
        'passed': mul_assoc,
        'check_needed': f'Verify $(a \\cdot b) \\cdot c \\equiv a \\cdot (b \\cdot c) \\pmod{{{p}}}$ for all triplets.',
        'proof': f'Modular multiplication is associative across all {p**3} element combinations.'
    })

    # 8. Multiplication Commutativity
    mul_comm = all((a * b) % p == (b * a) % p for a in elements for b in elements)
    axioms.append({
        'name': 'Multiplicative Commutativity',
        'symbol': r'a \cdot b = b \cdot a',
        'passed': mul_comm,
        'check_needed': f'Verify $a \\cdot b \\equiv b \\cdot a \\pmod{{{p}}}$ for all elements.',
        'proof': f'The multiplication table for {field_notation} is completely symmetric across its main diagonal.'
    })

    # 9. Multiplicative Identity (1)
    has_mul_id = all((a * 1) % p == a for a in elements)
    axioms.append({
        'name': 'Multiplicative Identity',
        'symbol': f'\\exists 1 \\in {latex_field} \\; \\text{{s.t.}} \\; a \\cdot 1 = a',
        'passed': has_mul_id,
        'check_needed': f'Check if element $1$ satisfies $a \\cdot 1 \\equiv a \\pmod{{{p}}}$ for all $a$.',
        'proof': f'1 acts as the unique multiplicative identity element in {field_notation}.'
    })

    # 10. Multiplicative Inverse for non-zero elements
    has_all_mul_inv = len(zero_divisors) == 0
    if is_field:
        mul_inv_proof = f"Every non-zero element $a \\in \\{{1, \\dots, {p-1}\\}}$ has a unique multiplicative inverse $a^{{-1}} \\pmod{{{p}}}$ since $\\gcd(a, {p}) = 1$."
    else:
        mul_inv_proof = f"FAILED: Modulus {p} is composite. Non-zero elements {zero_divisors} share common factors with {p} and lack multiplicative inverses (zero-divisors)."

    axioms.append({
        'name': 'Multiplicative Inverse (Non-Zero)',
        'symbol': r'\forall a \neq 0, \; \exists a^{-1} \text{ s.t. } a \cdot a^{-1} = 1',
        'passed': has_all_mul_inv,
        'check_needed': f'Verify that every non-zero element $a \\in {field_notation} \\setminus \\{{0\\}}$ has a multiplicative inverse $a^{{-1}}$.',
        'proof': mul_inv_proof
    })



    # 11. Distributivity
    distrib = all((a * ((b + c) % p)) % p == ((a * b) + (a * c)) % p for a in elements for b in elements for c in elements)
    axioms.append({
        'name': 'Distributive Law',
        'symbol': r'a \cdot (b + c) = (a \cdot b) + (a \cdot c)',
        'passed': distrib,
        'check_needed': f'Verify $a \\cdot (b + c) \\equiv (a \\cdot b) + (a \\cdot c) \\pmod{{{p}}}$ for all triplets.',
        'proof': f'Multiplication distributes over addition for all {p**3} element combinations in {field_notation}.'
    })

    # Final Conclusion Text
    if is_field:
        conclusion_title = f"{field_notation} IS A VALID FINITE FIELD"
        conclusion_text = f"All 11 required field axioms are satisfied. Hence {field_notation} = \\{{{', '.join(map(str, elements))}\\}} forms a valid Galois Field \\mathbb{{F}}_{{{p}}} under addition and multiplication modulo {p}."
    else:
        conclusion_title = f"Z_{{{p}}} IS NOT A FIELD (COMMUTATIVE RING WITH ZERO DIVISORS)"
        conclusion_text = f"Modulus {p} is composite (not prime). Non-zero elements {zero_divisors} lack multiplicative inverses because \\gcd(a, {p}) > 1. Thus, \\mathbb{{Z}}_{{{p}}} is a Commutative Ring with Unity, not a Field."

    return {
        'modulus': p,
        'field_notation': field_notation,
        'latex_field': latex_field,
        'is_field': is_field,
        'elements': elements,
        'add_table': add_table,
        'mul_table': mul_table,
        'add_inverses': add_inverses,
        'add_inverses_latex': add_inverses_latex,
        'mul_inverses': mul_inverses,
        'mul_inverses_latex': mul_inverses_latex,
        'zero_divisors': zero_divisors,
        'axioms': axioms,
        'conclusion_title': conclusion_title,
        'conclusion_text': conclusion_text,
        'task': task
    }

def analyze_gf2_field():
    """Backward compatibility wrapper for F_2."""
    return analyze_galois_field(2)

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
        'latex': formula_latex,
        'explanation': explanation
    }

compute_gf2_calc = solve_gf2_arithmetic

# ==========================================
# UNIT 1 - TOPIC 3: Vectors (Dot & Cross Product)
# ==========================================
def compute_vector_operations(v1_list, v2_list):
    """
    Computes 3D Vector operations: Dot product, Cross product, Angles, Projections.
    All outputs strictly formatted to max 2 decimal places.
    """
    v1 = np.array(v1_list, dtype=float)
    v2 = np.array(v2_list, dtype=float)

    mag1 = np.linalg.norm(v1)
    mag2 = np.linalg.norm(v2)

    dot_prod = np.dot(v1, v2)
    cross_prod = np.cross(v1, v2)
    cross_mag = np.linalg.norm(cross_prod)

    # Step-by-step LaTeX strings formatted to max 2 decimal places
    step_dot_latex = rf"\mathbf{{u}} \cdot \mathbf{{v}} = ({clean_val_str(v1[0])} \cdot {clean_val_str(v2[0])}) + ({clean_val_str(v1[1])} \cdot {clean_val_str(v2[1])}) + ({clean_val_str(v1[2])} \cdot {clean_val_str(v2[2])}) = {clean_val_str(v1[0]*v2[0])} + {clean_val_str(v1[1]*v2[1])} + {clean_val_str(v1[2]*v2[2])} = {round(float(dot_prod), 2)}"
    
    step_mag1_latex = rf"\|\mathbf{{u}}\| = \sqrt{{({clean_val_str(v1[0])})^2 + ({clean_val_str(v1[1])})^2 + ({clean_val_str(v1[2])})^2}} = \sqrt{{{round(float(v1[0]**2 + v1[1]**2 + v1[2]**2), 2)}}} = {round(float(mag1), 2)}"
    step_mag2_latex = rf"\|\mathbf{{v}}\| = \sqrt{{({clean_val_str(v2[0])})^2 + ({clean_val_str(v2[1])})^2 + ({clean_val_str(v2[2])})^2}} = \sqrt{{{round(float(v2[0]**2 + v2[1]**2 + v2[2]**2), 2)}}} = {round(float(mag2), 2)}"

    # Cross product 3x3 expansion
    c_i = v1[1]*v2[2] - v1[2]*v2[1]
    c_j = v1[2]*v2[0] - v1[0]*v2[2]
    c_k = v1[0]*v2[1] - v1[1]*v2[0]
    step_cross_latex = (
        r"\mathbf{u} \times \mathbf{v} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ "
        + f"{clean_val_str(v1[0])} & {clean_val_str(v1[1])} & {clean_val_str(v1[2])} \\ {clean_val_str(v2[0])} & {clean_val_str(v2[1])} & {clean_val_str(v2[2])}"
        + r" \end{vmatrix} = \left( (" + f"{clean_val_str(v1[1])}" + r")\cdot(" + f"{clean_val_str(v2[2])}" + r") - (" + f"{clean_val_str(v1[2])}" + r")\cdot(" + f"{clean_val_str(v2[1])}" + r") \right)\mathbf{i} - \left( (" + f"{clean_val_str(v1[0])}" + r")\cdot(" + f"{clean_val_str(v2[2])}" + r") - (" + f"{clean_val_str(v1[2])}" + r")\cdot(" + f"{clean_val_str(v2[0])}" + r") \right)\mathbf{j} + \left( (" + f"{clean_val_str(v1[0])}" + r")\cdot(" + f"{clean_val_str(v2[1])}" + r") - (" + f"{clean_val_str(v1[1])}" + r")\cdot(" + f"{clean_val_str(v2[0])}" + r") \right)\mathbf{k} = "
        + f"{round(c_i, 2)}" + r"\mathbf{i} + (" + f"{round(c_j, 2)}" + r")\mathbf{j} + (" + f"{round(c_k, 2)}" + r")\mathbf{k}"
    )

    # Angle calculation
    if mag1 > 0 and mag2 > 0:
        cos_theta = np.clip(dot_prod / (mag1 * mag2), -1.0, 1.0)
        angle_rad = np.arccos(cos_theta)
        angle_deg = np.degrees(angle_rad)
        step_angle_latex = rf"\cos(\theta) = \frac{{\mathbf{{u}} \cdot \mathbf{{v}}}}{{\|\mathbf{{u}}\| \|\mathbf{{v}}\|}} = \frac{{{round(float(dot_prod), 2)}}}{{{round(float(mag1), 2)} \cdot {round(float(mag2), 2)}}} = {round(float(cos_theta), 2)} \implies \theta = {round(float(angle_deg), 2)}^\circ"
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
            + f"{round(float(dot_prod), 2)}" + r"}{" + f"{round(float(mag2**2), 2)}" + r"} \begin{bmatrix} "
            + f"{clean_val_str(v2[0])} \\ {clean_val_str(v2[1])} \\ {clean_val_str(v2[2])}" + r" \end{bmatrix} = \begin{bmatrix} "
            + f"{round(float(proj_vector[0]), 2)} \\ {round(float(proj_vector[1]), 2)} \\ {round(float(proj_vector[2]), 2)}" + r" \end{bmatrix}"
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
        'mag1': round(float(mag1), 2),
        'mag2': round(float(mag2), 2),
        'unit_v1': np.round(unit_v1, 2).tolist(),
        'unit_v2': np.round(unit_v2, 2).tolist(),
        'dot_prod': round(float(dot_prod), 2),
        'cross_prod': np.round(cross_prod, 2).tolist(),
        'cross_mag': round(float(cross_mag), 2),
        'angle_rad': round(float(angle_rad), 2),
        'angle_deg': round(float(angle_deg), 2),
        'proj_vector': np.round(proj_vector, 2).tolist(),
        'proj_scalar': round(float(proj_scalar), 2),
        'is_orthogonal': bool(is_orthogonal),
        'is_parallel': bool(is_parallel),
        'triangle_area': round(float(cross_mag / 2.0), 2),
        'parallelepiped_area': round(float(cross_mag), 2),
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
    All decimal outputs formatted strictly to max 2 decimal places.
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
                rf"\text{{proj}}_{{\mathbf{{u}}_{{{j+1}}}}}(\mathbf{{v}}_{{{i+1}}}) = \frac{{\mathbf{{v}}_{{{i+1}}} \cdot \mathbf{{u}}_{{{j+1}}}}}{{\|\mathbf{{u}}_{{{j+1}}}\|^2}} \mathbf{{u}}_{{{j+1}}} = \frac{{{sp.latex(clean_val_2dp(dot_v_u))}}}{{{sp.latex(clean_val_2dp(dot_u_u))}}} {matrix_to_latex(u_j)} = {matrix_to_latex(proj_vec)}"
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
            'u_norm_latex': sp.latex(clean_val_2dp(u_norm)),
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
                'sum_row_col': (r + 1) + (c + 1),
                'entry': sp.latex(clean_val_2dp(val)),
                'sign': f"(-1)^{{{r+1}+{c+1}}} = {sign}",
                'submatrix_latex': matrix_to_latex(sub_mat),
                'minor_det_latex': sp.latex(clean_val_2dp(minor_det)),
                'cofactor_latex': sp.latex(clean_val_2dp(cofactor)),
                'term_latex': rf"({sp.latex(clean_val_2dp(val))}) \cdot ({sp.latex(clean_val_2dp(cofactor))}) = {sp.latex(clean_val_2dp(term_val))}"
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
                'sum_row_col': (r + 1) + (c + 1),
                'entry': sp.latex(clean_val_2dp(val)),
                'sign': f"(-1)^{{{r+1}+{c+1}}} = {sign}",
                'submatrix_latex': matrix_to_latex(sub_mat),
                'minor_det_latex': sp.latex(clean_val_2dp(minor_det)),
                'cofactor_latex': sp.latex(clean_val_2dp(cofactor)),
                'term_latex': rf"({sp.latex(clean_val_2dp(val))}) \cdot ({sp.latex(clean_val_2dp(cofactor))}) = {sp.latex(clean_val_2dp(term_val))}"
            })

    # Checkerboard sign matrix
    sign_matrix = [[f"+1" if (i+j)%2==0 else "-1" for j in range(n)] for i in range(n)]

    return {
        'matrix_latex': matrix_to_latex(mat),
        'expand_by': expand_by,
        'index': idx + 1,
        'terms': terms,
        'total_det_latex': sp.latex(clean_val_2dp(total_det)),
        'sign_matrix_latex': matrix_to_latex(sp.Matrix(sign_matrix))
    }

# ==========================================
# UNIT 2 - TOPIC 3: Eigenvalues, Eigenvectors & Diagonalization
# ==========================================
def solve_diagonalization(matrix_data):
    """
    Calculates Characteristic Polynomial, Eigenvalues, Eigenvectors, 
    and checks Diagonalization A = P D P^-1 with max 2 decimal places.
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
            'eigenvalue_latex': sp.latex(clean_val_2dp(val)),
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
        'char_poly_latex': sp.latex(clean_val_2dp(sp.expand(char_poly))),
        'eigenvalues_summary': eigenvalues_summary,
        'is_diagonalizable': is_diagonalizable,
        'P_latex': matrix_to_latex(P_mat) if P_mat else r"\text{N/A}",
        'D_latex': matrix_to_latex(D_mat) if D_mat else r"\text{N/A}",
        'P_inv_latex': matrix_to_latex(P_inv) if P_inv else r"\text{N/A}",
        'verification_latex': matrix_to_latex(verification_mat) if verification_mat else r"\text{N/A}"
    }


# ==============================================================================
# UNIT 3 - TOPIC 3.1: Integers, Primes & Divisibility
# ==============================================================================

def format_prime_factorization_latex(factor_dict: dict) -> str:
    """Formats a prime factorization dictionary into a LaTeX multiplication string."""
    parts = []
    for prime, power in sorted(factor_dict.items()):
        if power == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{{{power}}}")
    return r" \times ".join(parts) if parts else "1"

def format_prime_factorization_plain(factor_dict: dict) -> str:
    """Formats prime factorization into unicode plain text."""
    parts = []
    for prime, power in sorted(factor_dict.items()):
        if power == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{power}")
    return " × ".join(parts) if parts else "1"

def solve_divisibility(n: int):
    """
    Analyzes integer divisibility, prime factorization, divisor list, 
    number of divisors tau(n), and sum of divisors sigma(n).
    """
    n = abs(int(n))
    if n <= 1:
        return {
            'n': n,
            'is_valid': False,
            'error': f"Integer n = {n} must be greater than 1 for prime factorization analysis.",
            'steps': [],
            'solution_summary': "n > 1 required",
            'solution_latex': r"\text{Input must be an integer } n > 1"
        }

    steps = []
    steps.append({
        'title': 'Input Specification',
        'latex': fr"n = {n}",
        'explanation': f"Analyze integer properties, prime factorization, and divisor counts for n = {n}."
    })

    is_prime = sp.isprime(n)
    steps.append({
        'title': 'Primality Test',
        'latex': fr"n = {n} \implies \text{{{ 'Prime Number' if is_prime else 'Composite Number' }}}",
        'explanation': f"Testing whether {n} has any divisors other than 1 and itself. Result: {'Prime number' if is_prime else 'Composite number'}."
    })

    factors = factorint(n)
    fact_plain = format_prime_factorization_plain(factors)
    fact_latex = format_prime_factorization_latex(factors)
    steps.append({
        'title': 'Fundamental Theorem of Arithmetic (Prime Factorization)',
        'latex': fr"{n} = {fact_latex}",
        'explanation': f"Every integer greater than 1 can be represented uniquely as a product of prime powers: {n} = {fact_plain}."
    })

    div_list = sorted(sp.divisors(n))
    tau = len(div_list)
    sigma = sum(div_list)

    steps.append({
        'title': 'Divisor Enumeration & Counting Functions',
        'latex': fr"\tau({n}) = {tau}, \quad \sigma({n}) = {sigma}",
        'explanation': f"Positive divisors of {n}: {', '.join(map(str, div_list))}. Total number of divisors is tau({n}) = {tau}. Sum of all divisors is sigma({n}) = {sigma}."
    })

    ans_latex = fr"{n} = {fact_latex} \implies \tau({n}) = {tau}, \quad \sigma({n}) = {sigma}"
    ans_summary = f"{n} is {'Prime' if is_prime else 'Composite'}. {n} = {fact_plain} with {tau} divisors totaling {sigma}."

    return {
        'n': n,
        'is_valid': True,
        'is_prime': is_prime,
        'factors': factors,
        'divisors': div_list,
        'tau': tau,
        'sigma': sigma,
        'fact_plain': fact_plain,
        'fact_latex': fact_latex,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }


# ==============================================================================
# UNIT 3 - TOPIC 3.2: Euclidean Algorithm & Extended GCD (Bézout Identity)
# ==============================================================================

def compute_extended_euclidean_table(a: int, b: int):
    """Computes step-by-step rows for the Extended Euclidean Algorithm Table."""
    a_orig, b_orig = a, b
    rows = []
    r0, r1 = a, b
    x0, x1 = 1, 0
    y0, y1 = 0, 1

    rows.append({
        "step": 0, "dividend": a_orig, "divisor": b_orig,
        "q": "—", "r": r0, "x": x0, "y": y0, "is_gcd": False
    })
    rows.append({
        "step": 1, "dividend": a_orig, "divisor": b_orig,
        "q": "—", "r": r1, "x": x1, "y": y1, "is_gcd": False
    })

    step_i = 2
    last_gcd_idx = -1
    while r1 != 0:
        q = r0 // r1
        r2 = r0 % r1
        x2 = x0 - q * x1
        y2 = y0 - q * y1

        is_last_nonzero = (r2 == 0)
        rows.append({
            "step": step_i, "dividend": r0, "divisor": r1,
            "q": q, "r": r2, "x": x2, "y": y2, "is_gcd": False
        })
        if is_last_nonzero:
            last_gcd_idx = len(rows) - 2

        r0, r1 = r1, r2
        x0, x1 = x1, x2
        y0, y1 = y1, y2
        step_i += 1

    if last_gcd_idx >= 0:
        rows[last_gcd_idx]["is_gcd"] = True

    return rows

def solve_gcd_euclidean(a: int, b: int):
    """Computes GCD of two integers using the Euclidean Algorithm and Extended Bézout Identity."""
    a_abs, b_abs = abs(int(a)), abs(int(b))
    if a_abs == 0 and b_abs == 0:
        return {
            'is_valid': False,
            'error': "gcd(0, 0) is mathematically undefined.",
            'steps': [],
            'solution_summary': "Undefined",
            'solution_latex': r"\gcd(0, 0) \text{ is undefined}"
        }

    steps = []
    orig_a, orig_b = a_abs, b_abs
    if a_abs < b_abs:
        a_abs, b_abs = b_abs, a_abs
        steps.append({
            'title': 'Ordering Inputs',
            'latex': fr"a = {a_abs}, \quad b = {b_abs}",
            'explanation': f"Set a ≥ b for the standard Euclidean division algorithm steps."
        })

    steps.append({
        'title': 'Initial Setup for Euclidean Division',
        'latex': fr"\gcd({a_abs}, {b_abs})",
        'explanation': fr"Apply repeated division with remainder: r_{{i-1}} = q_i \cdot r_i + r_{{i+1}} until the remainder becomes 0."
    })

    r_prev, r_curr = a_abs, b_abs
    step_num = 1
    gcd_val = b_abs

    while r_curr != 0:
        q = r_prev // r_curr
        r_next = r_prev % r_curr
        steps.append({
            'title': f"Division Step {step_num}",
            'latex': fr"{r_prev} = {r_curr} \times {q} + {r_next}",
            'explanation': f"Dividing {r_prev} by {r_curr} yields quotient q = {q} and remainder r = {r_next}."
        })
        if r_next != 0:
            gcd_val = r_next
        r_prev, r_curr = r_curr, r_next
        step_num += 1

    if b_abs == 0:
        gcd_val = a_abs

    g, x, y = gcdex(a_abs, b_abs)
    bezout_str = f"{a_abs}({int(x)}) + {b_abs}({int(y)}) = {int(g)}"
    steps.append({
        'title': "Bézout's Identity (Extended Euclidean Algorithm)",
        'latex': fr"{a_abs}({int(x)}) + {b_abs}({int(y)}) = {int(g)}",
        'explanation': f"Linear combination of {a_abs} and {b_abs} yielding their GCD: coefficient s = {int(x)}, t = {int(y)}."
    })

    table_rows = compute_extended_euclidean_table(a_abs, b_abs)
    lcm_val = (a_abs * b_abs) // gcd_val if gcd_val else 0

    ans_latex = fr"\gcd({orig_a}, {orig_b}) = {int(gcd_val)} \implies {orig_a}({int(x)}) + {orig_b}({int(y)}) = {int(gcd_val)}"
    ans_summary = f"gcd({orig_a}, {orig_b}) = {int(gcd_val)}, LCM = {lcm_val}. Bézout identity: {bezout_str}."

    return {
        'is_valid': True,
        'a': orig_a,
        'b': orig_b,
        'gcd': int(gcd_val),
        'lcm': int(lcm_val),
        'x': int(x),
        'y': int(y),
        'bezout_str': bezout_str,
        'table_rows': table_rows,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }


# ==============================================================================
# UNIT 4 - TOPIC 4.1: Complex Numbers & Polar Form (Argand Diagram)
# ==============================================================================

def plot_argand_diagram_plotly(a: float, b: float):
    """Generates an interactive Plotly Argand plane diagram for complex number z = a + bi."""
    r = math.hypot(a, b)
    theta_deg = math.degrees(math.atan2(b, a))
    max_val = max(abs(a), abs(b), 1.0) * 1.35

    fig = go.Figure()
    # Real and Imaginary Axes
    fig.add_trace(go.Scatter(x=[-max_val, max_val], y=[0, 0], mode='lines', line=dict(color='rgba(255,255,255,0.25)', width=1.5), showlegend=False))
    fig.add_trace(go.Scatter(x=[0, 0], y=[-max_val, max_val], mode='lines', line=dict(color='rgba(255,255,255,0.25)', width=1.5), showlegend=False))

    # Reference Circle of Radius r
    circle_theta = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(x=r * np.cos(circle_theta), y=r * np.sin(circle_theta), mode='lines', line=dict(color='rgba(46, 196, 182, 0.25)', width=1, dash='dot'), name=f"|z| = {r:.2f} Circle"))

    # Vector line from origin
    fig.add_trace(go.Scatter(x=[0, a], y=[0, b], mode='lines+markers', line=dict(color='#2EC4B6', width=3), marker=dict(size=[0, 12], color='#2EC4B6'), name=f"z = {a:.2f} + {b:.2f}i"))

    # Dotted projection lines
    fig.add_trace(go.Scatter(x=[a, a], y=[0, b], mode='lines', line=dict(color='#FFB627', width=1.5, dash='dash'), showlegend=False))
    fig.add_trace(go.Scatter(x=[0, a], y=[b, b], mode='lines', line=dict(color='#FFB627', width=1.5, dash='dash'), showlegend=False))

    fig.update_layout(
        title=dict(text=f"Argand Plane: z = {a} + {b}i (Modulus r = {r:.2f}, θ = {theta_deg:.1f}°)", font=dict(color='#FFFFFF', size=15)),
        xaxis=dict(title="Real Axis (Re)", gridcolor='rgba(255,255,255,0.08)', range=[-max_val, max_val], color='#FFFFFF'),
        yaxis=dict(title="Imaginary Axis (Im)", gridcolor='rgba(255,255,255,0.08)', range=[-max_val, max_val], color='#FFFFFF', scaleanchor="x", scaleratio=1),
        paper_bgcolor='rgba(15, 23, 42, 0.8)',
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        font=dict(color='#F7F5EF', family='Outfit, sans-serif'),
        height=380,
        margin=dict(l=30, r=30, t=50, b=30)
    )
    return fig

def solve_complex_to_polar(a: float, b: float):
    """Converts a rectangular complex number z = a + bi into polar and Euler forms with steps and Argand plot."""
    a = float(a)
    b = float(b)
    steps = []

    steps.append({
        'title': 'Input Rectangular Form',
        'latex': fr"z = {clean_val_str(a)} + {clean_val_str(b)}i",
        'explanation': f"Cartesian coordinates in the complex plane: Real component Re(z) = {clean_val_str(a)}, Imaginary component Im(z) = {clean_val_str(b)}."
    })

    r = math.hypot(a, b)
    steps.append({
        'title': 'Modulus (Magnitude) Calculation',
        'latex': fr"|z| = r = \sqrt{{a^2 + b^2}} = \sqrt{{({clean_val_str(a)})^2 + ({clean_val_str(b)})^2}} = {r:.4f}",
        'explanation': f"Euclidean distance from the origin (0, 0) to the point ({clean_val_str(a)}, {clean_val_str(b)}) on the Argand plane."
    })

    theta_rad = math.atan2(b, a)
    theta_deg = math.degrees(theta_rad)
    steps.append({
        'title': 'Argument (Phase Angle) Calculation',
        'latex': fr"\theta = \operatorname{{atan2}}({clean_val_str(b)}, {clean_val_str(a)}) = {theta_rad:.4f}\text{{ rad}} = {theta_deg:.2f}^\circ",
        'explanation': f"The counter-clockwise angle formed with the positive real axis. Principal value in (-π, π]."
    })

    conj_latex = fr"\bar{{z}} = {clean_val_str(a)} - {clean_val_str(b)}i"
    steps.append({
        'title': 'Complex Conjugate',
        'latex': conj_latex,
        'explanation': f"Reflected across the horizontal real axis: sign of the imaginary component is negated."
    })

    polar_str = f"{r:.4f} (cos {theta_deg:.2f}° + i sin {theta_deg:.2f}°)"
    exp_latex = fr"z = {r:.4f} \left(\cos({theta_deg:.2f}^\circ) + i\sin({theta_deg:.2f}^\circ)\right) = {r:.4f} e^{{{theta_deg:.2f}^\circ i}}"
    
    steps.append({
        'title': 'Polar & Euler Trigonometric Representation',
        'latex': exp_latex,
        'explanation': f"Expressed in trigonometric polar form and Euler's exponential form."
    })

    fig = plot_argand_diagram_plotly(a, b)
    plot_html = fig.to_html(full_html=False, include_plotlyjs=False) if fig else ""

    ans_latex = exp_latex
    ans_summary = f"Modulus r = {r:.4f}, Argument θ = {theta_deg:.2f}° ({theta_rad:.4f} rad), Conjugate = {clean_val_str(a)} - {clean_val_str(b)}i."

    return {
        'is_valid': True,
        'a': a,
        'b': b,
        'r': r,
        'theta_rad': theta_rad,
        'theta_deg': theta_deg,
        'polar_str': polar_str,
        'exp_latex': exp_latex,
        'conj_latex': conj_latex,
        'plot_html': plot_html,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }


# ==============================================================================
# UNIT 4 - TOPIC 4.2: De Moivre's Theorem & Complex Roots
# ==============================================================================

def plot_complex_roots_plotly(a: float, b: float, n: int, roots: list, r_root: float):
    """Generates an interactive Plotly diagram displaying the n-th roots polygon on the complex plane."""
    fig = go.Figure()
    max_val = max(abs(a), abs(b), r_root, 1.0) * 1.35

    # Axes
    fig.add_trace(go.Scatter(x=[-max_val, max_val], y=[0, 0], mode='lines', line=dict(color='rgba(255,255,255,0.25)', width=1.5), showlegend=False))
    fig.add_trace(go.Scatter(x=[0, 0], y=[-max_val, max_val], mode='lines', line=dict(color='rgba(255,255,255,0.25)', width=1.5), showlegend=False))

    # Roots circle
    circle_theta = np.linspace(0, 2*np.pi, 120)
    fig.add_trace(go.Scatter(x=r_root * np.cos(circle_theta), y=r_root * np.sin(circle_theta), mode='lines', line=dict(color='rgba(46, 196, 182, 0.35)', width=1.5, dash='dot'), name=f"Radius R = {r_root:.2f}"))

    # Polygon connecting roots
    poly_x = [rt['re'] for rt in roots] + [roots[0]['re']]
    poly_y = [rt['im'] for rt in roots] + [roots[0]['im']]
    fig.add_trace(go.Scatter(x=poly_x, y=poly_y, mode='lines', line=dict(color='rgba(255, 182, 39, 0.6)', width=2), name=f"Regular {n}-gon"))

    # Roots vertices
    for rt in roots:
        k = rt['k']
        fig.add_trace(go.Scatter(
            x=[0, rt['re']], y=[0, rt['im']],
            mode='lines+markers',
            line=dict(color='#2EC4B6', width=2),
            marker=dict(size=[0, 10], color='#2EC4B6'),
            name=f"Root w_{k}"
        ))

    fig.update_layout(
        title=dict(text=f"Complex {n}-th Roots Regular Polygon (Radius R = {r_root:.2f})", font=dict(color='#FFFFFF', size=15)),
        xaxis=dict(title="Real Axis (Re)", gridcolor='rgba(255,255,255,0.08)', range=[-max_val, max_val], color='#FFFFFF'),
        yaxis=dict(title="Imaginary Axis (Im)", gridcolor='rgba(255,255,255,0.08)', range=[-max_val, max_val], color='#FFFFFF', scaleanchor="x", scaleratio=1),
        paper_bgcolor='rgba(15, 23, 42, 0.8)',
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        font=dict(color='#F7F5EF', family='Outfit, sans-serif'),
        height=400,
        margin=dict(l=30, r=30, t=50, b=30)
    )
    return fig

def solve_demoivre(a: float, b: float, n: int, mode: str = 'powers'):
    """Applies De Moivre's Theorem to compute integer powers (z^n) or n-th roots (z^(1/n)) of complex numbers."""
    a = float(a)
    b = float(b)
    n = int(n)
    if n <= 0:
        n = 1

    r = math.hypot(a, b)
    theta = math.atan2(b, a)
    theta_deg = math.degrees(theta)

    steps = []
    steps.append({
        'title': 'Original Complex Number in Polar Form',
        'latex': fr"z = {clean_val_str(a)} + {clean_val_str(b)}i = {r:.4f} \left(\cos({theta_deg:.2f}^\circ) + i\sin({theta_deg:.2f}^\circ)\right)",
        'explanation': f"Modulus r = {r:.4f}, argument theta = {theta_deg:.2f}°."
    })

    if mode == 'powers':
        # z^n = r^n (cos(n theta) + i sin(n theta))
        r_n = r ** n
        n_theta = n * theta
        n_theta_deg = math.degrees(n_theta) % 360
        re_part = r_n * math.cos(n_theta)
        im_part = r_n * math.sin(n_theta)

        steps.append({
            'title': "De Moivre's Theorem for Powers",
            'latex': fr"z^n = [r (\cos\theta + i\sin\theta)]^n = r^n \left(\cos(n\theta) + i\sin(n\theta)\right)",
            'explanation': f"Raise modulus to power n = {n} and multiply phase angle by {n}."
        })
        steps.append({
            'title': 'Substitution & Calculation',
            'latex': fr"z^{{{n}}} = ({r:.4f})^{{{n}}} \left(\cos({n} \times {theta_deg:.2f}^\circ) + i\sin({n} \times {theta_deg:.2f}^\circ)\right) = {r_n:.4f} \left(\cos({n_theta_deg:.2f}^\circ) + i\sin({n_theta_deg:.2f}^\circ)\right)",
            'explanation': f"Resulting modulus is {r_n:.4f}, resulting angle is {n_theta_deg:.2f}°."
        })
        steps.append({
            'title': 'Rectangular Form Result',
            'latex': fr"z^{{{n}}} = {clean_val_str(round(re_part, 2))} + {clean_val_str(round(im_part, 2))}i",
            'explanation': f"Converting back to Cartesian components: Re = {re_part:.4f}, Im = {im_part:.4f}."
        })

        ans_latex = fr"z^{{{n}}} = {r_n:.4f} e^{{{n_theta_deg:.2f}^\circ i}} = {clean_val_str(round(re_part, 2))} + {clean_val_str(round(im_part, 2))}i"
        ans_summary = f"z^{n} = {re_part:.2f} + {im_part:.2f}i with modulus {r_n:.2f} and angle {n_theta_deg:.2f}°."

        fig = plot_argand_diagram_plotly(re_part, im_part)
        plot_html = fig.to_html(full_html=False, include_plotlyjs=False) if fig else ""

        return {
            'is_valid': True,
            'mode': 'powers',
            'n': n,
            'r_n': r_n,
            're_part': re_part,
            'im_part': im_part,
            'plot_html': plot_html,
            'steps': steps,
            'solution_summary': ans_summary,
            'solution_latex': ans_latex
        }
    else:
        # n-th roots: w_k = r^(1/n) (cos((theta + 2k pi)/n) + i sin((theta + 2k pi)/n)) for k = 0, ..., n-1
        r_root = r ** (1.0 / n)
        roots = []
        steps.append({
            'title': "De Moivre's Theorem for n-th Roots Formula",
            'latex': fr"w_k = \sqrt[{n}]{{r}} \left(\cos\left(\frac{{\theta + 2k\pi}}{{{n}}}\right) + i\sin\left(\frac{{\theta + 2k\pi}}{{{n}}}\right)\right), \quad k = 0, 1, \dots, {n-1}",
            'explanation': f"There are exactly {n} distinct complex roots spaced equally by 360°/{n} = {360/n:.2f}° around a circle of radius {r_root:.4f}."
        })

        root_rows = []
        for k in range(n):
            k_angle_rad = (theta + 2 * math.pi * k) / n
            k_angle_deg = math.degrees(k_angle_rad) % 360
            x_k = r_root * math.cos(k_angle_rad)
            y_k = r_root * math.sin(k_angle_rad)
            roots.append({'k': k, 'angle_deg': k_angle_deg, 're': x_k, 'im': y_k})
            root_rows.append(fr"w_{{{k}}} = {r_root:.3f} \left(\cos({k_angle_deg:.1f}^\circ) + i\sin({k_angle_deg:.1f}^\circ)\right) = {x_k:.2f} + {y_k:.2f}i")

        steps.append({
            'title': f"Calculated All {n} Distinct Roots",
            'latex': r" \\ ".join(root_rows),
            'explanation': f"All {n} roots form the vertices of a regular {n}-sided polygon on the Argand plane."
        })

        fig = plot_complex_roots_plotly(a, b, n, roots, r_root)
        plot_html = fig.to_html(full_html=False, include_plotlyjs=False) if fig else ""

        ans_latex = fr"\text{{Roots: }} w_k = {r_root:.3f} e^{{i \frac{{\theta + 2k\pi}}{{{n}}}}}, \ k \in [0, {n-1}]"
        ans_summary = f"Computed all {n} complex roots of magnitude {r_root:.4f} forming a regular {n}-gon."

        return {
            'is_valid': True,
            'mode': 'roots',
            'n': n,
            'r_root': r_root,
            'roots': roots,
            'plot_html': plot_html,
            'steps': steps,
            'solution_summary': ans_summary,
            'solution_latex': ans_latex
        }


# ==============================================================================
# UNIT 5: Combinatorics & Counting (Permutations & Combinations)
# ==============================================================================

def solve_permutations(n: int, r: int):
    """Computes Permutations P(n, r) and circular permutations (n-1)!."""
    n, r = int(n), int(r)
    if r < 0 or n < 0 or r > n:
        return {
            'is_valid': False,
            'error': f"Invalid parameters: n = {n}, r = {r}. Requirement: 0 ≤ r ≤ n.",
            'steps': [],
            'solution_summary': "Invalid parameters",
            'solution_latex': r"\text{Requirement: } 0 \le r \le n"
        }

    steps = []
    steps.append({
        'title': 'Permutation Formula Definition',
        'latex': fr"P(n, r) = {{}}^n P_r = \frac{{n!}}{{(n - r)!}}",
        'explanation': f"The number of ordered arrangements of {r} distinct items chosen from a set of {n} distinct items."
    })

    n_fact = math.factorial(n)
    nr_fact = math.factorial(n - r)
    npr = n_fact // nr_fact

    steps.append({
        'title': 'Constituent Factorial Calculations',
        'latex': fr"{n}! = {n_fact}, \quad ({n} - {r})! = {n - r}! = {nr_fact}",
        'explanation': f"Evaluating factorials n! and (n - r)!."
    })

    steps.append({
        'title': 'Quotient Evaluation',
        'latex': fr"P({n}, {r}) = \frac{{{n_fact}}}{{{nr_fact}}} = {npr}",
        'explanation': f"Dividing out the unselected (n - r) objects leaves exactly {npr} possible linear arrangements."
    })

    circ_perm = math.factorial(n - 1) if n >= 1 else 1
    steps.append({
        'title': 'Circular Permutations Note',
        'latex': fr"P_\text{{circular}}({n}) = (n - 1)! = ({n} - 1)! = {circ_perm}",
        'explanation': f"If arranging all {n} distinct items around a circle where rotational positions are equivalent, fixing one item yields (n - 1)! = {circ_perm} arrangements."
    })

    ans_latex = fr"P({n}, {r}) = \frac{{{n}!}}{{({n}-{r})!}} = {npr}, \quad P_\text{{circular}}({n}) = {circ_perm}"
    ans_summary = f"P({n}, {r}) = {npr}. Circular arrangement of {n} items is {circ_perm}."

    return {
        'is_valid': True,
        'n': n,
        'r': r,
        'npr': npr,
        'circ_perm': circ_perm,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }

def solve_combinations(n: int, r: int):
    """Computes Combinations C(n, r) with Pascal's identity and factorial steps."""
    n, r = int(n), int(r)
    if r < 0 or n < 0 or r > n:
        return {
            'is_valid': False,
            'error': f"Invalid parameters: n = {n}, r = {r}. Requirement: 0 ≤ r ≤ n.",
            'steps': [],
            'solution_summary': "Invalid parameters",
            'solution_latex': r"\text{Requirement: } 0 \le r \le n"
        }

    steps = []
    steps.append({
        'title': 'Combination Formula Definition',
        'latex': fr"C(n, r) = \binom{{n}}{{r}} = \frac{{n!}}{{r! (n - r)!}}",
        'explanation': f"The number of unordered selections (subsets) of {r} elements chosen from a collection of {n} elements."
    })

    n_fact = math.factorial(n)
    r_fact = math.factorial(r)
    nr_fact = math.factorial(n - r)
    ncr = math.comb(n, r)

    steps.append({
        'title': 'Factorial Evaluation',
        'latex': fr"{n}! = {n_fact}, \quad {r}! = {r_fact}, \quad ({n} - {r})! = {nr_fact}",
        'explanation': f"Evaluating constituent factorials."
    })

    steps.append({
        'title': 'Exact Computation',
        'latex': fr"\binom{{{n}}}{{{r}}} = \frac{{{n_fact}}}{{{r_fact} \times {nr_fact}}} = {ncr}",
        'explanation': f"Dividing the permutation count by r! to eliminate ordering redundancies."
    })

    steps.append({
        'title': "Pascal's Symmetry Identity",
        'latex': fr"\binom{{{n}}}{{{r}}} = \binom{{{n}}}{{{n - r}}} = {ncr}",
        'explanation': f"Selecting r elements to include is mathematically identical to selecting the (n - r) elements to omit."
    })

    ans_latex = fr"\binom{{{n}}}{{{r}}} = {ncr}"
    ans_summary = f"C({n}, {r}) = {ncr} unique subsets."

    return {
        'is_valid': True,
        'n': n,
        'r': r,
        'ncr': ncr,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }


# ==============================================================================
# UNIT 6: Functions & Set Theory (Mappings, Injective/Surjective/Bijective, Inverse Images)
# ==============================================================================

def plot_function_diagram_plotly(domain: list, codomain: list, mapping: dict, highlight_target_set: list = None):
    """Generates an interactive Plotly bipartite mapping diagram f: A -> B."""
    fig = go.Figure()
    d_x, d_y = [0] * len(domain), list(range(len(domain), 0, -1))
    c_x, c_y = [1] * len(codomain), list(range(len(codomain), 0, -1))

    domain_pos = {d: (0, y) for d, y in zip(domain, d_y)}
    codomain_pos = {c: (1, y) for c, y in zip(codomain, c_y)}

    for d, c in mapping.items():
        if d in domain_pos and c in codomain_pos:
            x0, y0 = domain_pos[d]
            x1, y1 = codomain_pos[c]
            is_hl = highlight_target_set and str(c) in highlight_target_set
            line_color = "#FFB627" if is_hl else "#2EC4B6"
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines+markers',
                line=dict(color=line_color, width=3 if is_hl else 2),
                hoverinfo='text',
                text=f"f({d}) = {c}",
                showlegend=False
            ))

    fig.add_trace(go.Scatter(
        x=[0] * len(domain), y=d_y,
        mode='markers+text',
        marker=dict(size=28, color='#14213D', line=dict(color='#2EC4B6', width=2)),
        text=domain, textposition="middle left",
        textfont=dict(color='#FFFFFF', size=14, family='Outfit, sans-serif'),
        name="Domain A", showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[1] * len(codomain), y=c_y,
        mode='markers+text',
        marker=dict(size=28, color='#14213D', line=dict(color='#FFB627', width=2)),
        text=codomain, textposition="middle right",
        textfont=dict(color='#FFFFFF', size=14, family='Outfit, sans-serif'),
        name="Codomain B", showlegend=False
    ))

    fig.update_layout(
        title=dict(text="Bipartite Function Mapping Diagram f: A → B", font=dict(color='#FFFFFF', size=15)),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 1.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(15, 23, 42, 0.8)',
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        height=320,
        margin=dict(l=20, r=20, t=45, b=20)
    )
    return fig

def solve_functions(domain: list, codomain: list, mapping: dict):
    """Classifies a function as Injective (one-to-one), Surjective (onto), or Bijective."""
    steps = []
    steps.append({
        'title': 'Function Sets Specification',
        'latex': fr"A = \{{{', '.join(map(str, domain))}\}}, \quad B = \{{{', '.join(map(str, codomain))}\}}",
        'explanation': f"Domain set A has {len(domain)} elements; Codomain set B has {len(codomain)} elements."
    })

    map_formatted = ", ".join(f"f({k}) = {v}" for k, v in mapping.items())
    steps.append({
        'title': 'Defined Element Mappings',
        'latex': fr"f: A \to B, \quad {map_formatted}",
        'explanation': f"Explicit relation assigning each element of domain A to an output in codomain B."
    })

    # Injective check
    mapped_vals = list(mapping.values())
    is_injective = (len(mapped_vals) == len(set(mapped_vals)))
    inj_reason = "All domain elements produce distinct codomain outputs (no collisions)." if is_injective else "Multiple domain elements map to the same codomain value."
    steps.append({
        'title': 'Injectivity (One-to-One) Test',
        'latex': fr"\text{{Injective: }} \mathbf{{{ 'YES' if is_injective else 'NO' }}}",
        'explanation': f"Condition: f(x_1) = f(x_2) implies x_1 = x_2. {inj_reason}"
    })

    # Surjective check
    range_set = set(mapped_vals)
    codomain_set = set(codomain)
    is_surjective = (range_set == codomain_set)
    unmapped = list(codomain_set - range_set)
    surj_reason = "The range equals the entire codomain (every element has a pre-image)." if is_surjective else f"Elements in codomain not mapped to: {unmapped}."
    steps.append({
        'title': 'Surjectivity (Onto) Test',
        'latex': fr"\text{{Surjective: }} \mathbf{{{ 'YES' if is_surjective else 'NO' }}}",
        'explanation': f"Condition: Range(f) = B. {surj_reason}"
    })

    # Bijective check
    is_bijective = (is_injective and is_surjective)
    steps.append({
        'title': 'Bijectivity (One-to-One Correspondence) Test',
        'latex': fr"\text{{Bijective: }} \mathbf{{{ 'YES' if is_bijective else 'NO' }}}",
        'explanation': f"Function is both one-to-one and onto. {'An inverse function f⁻¹ exists.' if is_bijective else 'The function is not invertible.'}"
    })

    class_type = "Bijective (One-to-One & Onto)" if is_bijective else "Injective (One-to-One only)" if is_injective else "Surjective (Onto only)" if is_surjective else "Neither Injective nor Surjective"

    fig = plot_function_diagram_plotly(domain, codomain, mapping)
    plot_html = fig.to_html(full_html=False, include_plotlyjs=False) if fig else ""

    ans_latex = fr"\text{{Classification: }} \mathbf{{{class_type}}}"
    ans_summary = f"{class_type}. Range = {{{', '.join(map(str, sorted(list(range_set))))}}}."

    return {
        'is_valid': True,
        'domain': domain,
        'codomain': codomain,
        'mapping': mapping,
        'is_injective': is_injective,
        'is_surjective': is_surjective,
        'is_bijective': is_bijective,
        'class_type': class_type,
        'range_set': sorted(list(range_set)),
        'unmapped': unmapped,
        'plot_html': plot_html,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }

def solve_inverse_image(domain: list, codomain: list, mapping: dict, target_set: list):
    """Computes the inverse image f⁻¹(S) of a target subset S ⊆ B."""
    target_clean = [str(x).strip() for x in target_set]
    inv_image = [str(k) for k, v in mapping.items() if str(v) in target_clean]

    steps = []
    steps.append({
        'title': 'Target Subset Specification',
        'latex': fr"S \subseteq B = \{{{', '.join(target_clean)}\}}",
        'explanation': f"We seek the inverse image (pre-image) f⁻¹(S) of the subset S in codomain B."
    })
    steps.append({
        'title': 'Inverse Image Definition',
        'latex': r"f^{-1}(S) = \{ x \in A \mid f(x) \in S \}",
        'explanation': "The set of all domain elements whose outputs fall into the target subset S."
    })

    eval_items = []
    for k, v in mapping.items():
        in_s = str(v) in target_clean
        eval_items.append(f"f({k}) = {v} {'∈ S (Include)' if in_s else '∉ S (Exclude)'}")
    steps.append({
        'title': 'Pre-Image Membership Testing',
        'latex': fr"\text{{Tested: }} {len(mapping)} \text{{ domain points}}",
        'explanation': " | ".join(eval_items)
    })

    inv_str = f"{{{', '.join(inv_image)}}}" if inv_image else r"\emptyset"
    steps.append({
        'title': 'Resulting Pre-Image Set',
        'latex': fr"f^{{-1}}(S) = {inv_str}",
        'explanation': f"The complete inverse image is {inv_str}."
    })

    fig = plot_function_diagram_plotly(domain, codomain, mapping, highlight_target_set=target_clean)
    plot_html = fig.to_html(full_html=False, include_plotlyjs=False) if fig else ""

    ans_latex = fr"f^{{-1}}(\{{{', '.join(target_clean)}\}}) = {inv_str}"
    ans_summary = f"Pre-image f⁻¹(S) = {inv_str}."

    return {
        'is_valid': True,
        'target_set': target_clean,
        'inverse_image': inv_image,
        'plot_html': plot_html,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }


# ==============================================================================
# UNIT 7: Calculus & Analysis (Limits & Continuity)
# ==============================================================================

def plot_limit_curve_plotly(expr, x_sym, c_val, limit_val=None):
    """Generates an interactive Plotly curve showing the behavior of f(x) approaching point c."""
    try:
        f_lambd = sp.lambdify(x_sym, expr, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'exp': np.exp, 'tan': np.tan}])
        x_vals = np.linspace(c_val - 4, c_val + 4, 300)
        x_vals = x_vals[np.abs(x_vals - c_val) > 0.001]
        y_vals = f_lambd(x_vals)
        mask = np.abs(y_vals) < 50
        x_plot = x_vals[mask]
        y_plot = y_vals[mask]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_plot, y=y_plot, mode='lines', line=dict(color='#2EC4B6', width=2.5), name="f(x)"))

        if limit_val is not None and abs(limit_val) < 50:
            fig.add_trace(go.Scatter(
                x=[c_val], y=[limit_val],
                mode='markers',
                marker=dict(size=12, color='#FFB627', symbol='circle-open', line=dict(color='#FFB627', width=3)),
                name=f"Limit Point ({c_val:.2f}, {limit_val:.2f})"
            ))

        fig.update_layout(
            title=dict(text=f"Function Curve around x = {c_val:.2f}", font=dict(color='#FFFFFF', size=15)),
            xaxis=dict(title=f"Variable {x_sym}", gridcolor='rgba(255,255,255,0.08)', color='#FFFFFF'),
            yaxis=dict(title="f(x)", gridcolor='rgba(255,255,255,0.08)', color='#FFFFFF'),
            paper_bgcolor='rgba(15, 23, 42, 0.8)',
            plot_bgcolor='rgba(15, 23, 42, 0.8)',
            font=dict(color='#F7F5EF', family='Outfit, sans-serif'),
            height=360,
            margin=dict(l=30, r=30, t=50, b=30)
        )
        return fig
    except Exception:
        return None

def solve_limits_continuity(expr_str: str, var_str: str = 'x', point_c: float = 0.0, direction: str = 'both'):
    """Performs symbolic limit computation, left/right hand limits, and continuity testing at point c."""
    try:
        x = sp.Symbol(var_str.strip() or 'x')
        expr = sp.sympify(expr_str)
        c = sp.sympify(point_c)
    except Exception as e:
        return {
            'is_valid': False,
            'error': f"Syntax error parsing mathematical expression: {e}",
            'steps': [],
            'solution_summary': "Parse Error",
            'solution_latex': r"\text{Expression syntax error}"
        }

    steps = []
    steps.append({
        'title': 'Input Function & Limit Point',
        'latex': fr"f({x}) = {sp.latex(expr)}, \quad x \to {sp.latex(c)}",
        'explanation': f"Evaluating limiting behavior of function f({x}) as {x} approaches {c}."
    })

    # Direct substitution check
    try:
        f_c = expr.subs(x, c)
        f_c_latex = sp.latex(clean_val_2dp(f_c))
        f_c_defined = not (f_c.has(sp.zoo) or f_c.has(sp.nan) or f_c.has(sp.oo) or f_c.has(-sp.oo))
    except Exception:
        f_c_latex = r"\text{Undefined}"
        f_c_defined = False

    steps.append({
        'title': 'Direct Substitution Test',
        'latex': fr"f({sp.latex(c)}) = {f_c_latex}",
        'explanation': f"Evaluating f({c}) directly. {'Defined.' if f_c_defined else 'Yields indeterminate / undefined form; limits or algebraic simplification required.'}"
    })

    # Left-hand limit: dir='-'
    lim_left = sp.limit(expr, x, c, dir='-')
    # Right-hand limit: dir='+'
    lim_right = sp.limit(expr, x, c, dir='+')
    # Two-sided limit
    lim_both = sp.limit(expr, x, c, dir='+-')

    lim_left_latex = sp.latex(clean_val_2dp(lim_left))
    lim_right_latex = sp.latex(clean_val_2dp(lim_right))
    lim_both_latex = sp.latex(clean_val_2dp(lim_both))

    steps.append({
        'title': 'One-Sided Limits (Left & Right)',
        'latex': fr"\lim_{{{x} \to {sp.latex(c)}^-}} f({x}) = {lim_left_latex}, \quad \lim_{{{x} \to {sp.latex(c)}^+}} f({x}) = {lim_right_latex}",
        'explanation': f"Left-hand approach limit is {lim_left_latex}; Right-hand approach limit is {lim_right_latex}."
    })

    limits_match = (lim_left == lim_right)
    steps.append({
        'title': 'Two-Sided Limit Existence',
        'latex': fr"\lim_{{{x} \to {sp.latex(c)}}} f({x}) = {lim_both_latex if limits_match else r'\text{Does Not Exist (DNE)}'}",
        'explanation': f"{'Left and right limits agree, so two-sided limit exists.' if limits_match else 'Left and right limits do not match, therefore two-sided limit does not exist.'}"
    })

    is_continuous = (f_c_defined and limits_match and (lim_both == f_c))
    cont_reason = "All 3 conditions met: f(c) is defined, limit exists, and lim = f(c)." if is_continuous else "Discontinuous at x = c."
    steps.append({
        'title': 'Continuity Verification at Point c',
        'latex': fr"\text{{Continuous at }} x = {sp.latex(c)}: \mathbf{{{ 'YES' if is_continuous else 'NO' }}}",
        'explanation': cont_reason
    })

    fig = plot_limit_curve_plotly(expr, x, float(c) if c.is_number else 0.0, float(lim_both) if lim_both.is_number else None)
    plot_html = fig.to_html(full_html=False, include_plotlyjs=False) if fig else ""

    ans_latex = fr"\lim_{{{x} \to {sp.latex(c)}}} f({x}) = {lim_both_latex if limits_match else r'\text{DNE}'}, \quad \text{{Continuous: }} \mathbf{{{ 'Yes' if is_continuous else 'No' }}}"
    ans_summary = f"Limit = {lim_both_latex if limits_match else 'DNE'}. Continuous at x = {c}: {'Yes' if is_continuous else 'No'}."

    return {
        'is_valid': True,
        'expr_latex': sp.latex(expr),
        'point_c': clean_val_str(c),
        'f_c_defined': f_c_defined,
        'f_c_latex': f_c_latex,
        'lim_left': lim_left_latex,
        'lim_right': lim_right_latex,
        'lim_both': lim_both_latex,
        'limits_match': limits_match,
        'is_continuous': is_continuous,
        'plot_html': plot_html,
        'steps': steps,
        'solution_summary': ans_summary,
        'solution_latex': ans_latex
    }


# ==============================================================================
# INTERACTIVE LAB: Procedural Math Quiz & AI Math Assistant
# ==============================================================================

def generate_procedural_question():
    """Generates procedural math practice questions across all syllabus topics."""
    topics_list = ["gcd", "divisibility", "complex", "perm", "comb", "functions"]
    t = random.choice(topics_list)

    if t == "gcd":
        a = random.randint(12, 120) * random.randint(2, 6)
        b = random.randint(12, 120) * random.randint(2, 6)
        ans = math.gcd(a, b)
        options = sorted(list({ans, ans + random.randint(1, 4), max(1, ans - random.randint(1, 4)), ans * 2}))
        return {
            "topic": "Euclidean GCD",
            "q": f"Compute the Greatest Common Divisor gcd({a}, {b}) using Euclid's division algorithm.",
            "options": [str(x) for x in options],
            "answer": str(ans),
            "exp": f"Applying Euclid's algorithm: gcd({a}, {b}) = {ans}."
        }
    elif t == "divisibility":
        n = random.choice([24, 36, 48, 60, 72, 90, 100, 120, 180, 360])
        tau = len(sp.divisors(n))
        options = sorted(list({tau, tau + 1, max(1, tau - 2), tau + 3}))
        return {
            "topic": "Divisibility & Primes",
            "q": f"How many positive integer divisors τ(n) does n = {n} have?",
            "options": [str(x) for x in options],
            "answer": str(tau),
            "exp": f"Prime factorization of {n} yields factor powers. τ({n}) = {tau}."
        }
    elif t == "complex":
        a, b = random.choice([(3, 4), (1, 1.732), (5, 12), (1, 1), (0, 4)])
        r = round(math.hypot(a, b), 2)
        options = sorted(list({r, round(r + 1.5, 2), round(max(0.5, r - 1.2), 2), round(r * 1.5, 2)}))
        return {
            "topic": "Complex Numbers",
            "q": f"Find the modulus r = |z| for complex number z = {a} + {b}i.",
            "options": [str(x) for x in options],
            "answer": str(r),
            "exp": f"Modulus r = √(a² + b²) = √({a}² + {b}²) = {r}."
        }
    elif t == "perm":
        n = random.randint(5, 8)
        r = random.randint(2, 4)
        ans = math.perm(n, r)
        options = sorted(list({ans, ans + 10, max(1, ans - 12), ans * 2}))
        return {
            "topic": "Permutations",
            "q": f"Calculate the number of permutations P({n}, {r}).",
            "options": [str(x) for x in options],
            "answer": str(ans),
            "exp": f"P({n}, {r}) = {n}! / ({n}-{r})! = {ans}."
        }
    elif t == "comb":
        n = random.randint(5, 9)
        r = random.randint(2, 4)
        ans = math.comb(n, r)
        options = sorted(list({ans, ans + 4, max(1, ans - 5), ans + 10}))
        return {
            "topic": "Combinations",
            "q": f"Calculate the number of combinations C({n}, {r}).",
            "options": [str(x) for x in options],
            "answer": str(ans),
            "exp": f"C({n}, {r}) = {n}! / ({r}! × ({n}-{r})!) = {ans}."
        }
    else:
        return {
            "topic": "Functions & Sets",
            "q": "If Domain A has 3 elements and Codomain B has 3 elements, and f maps each domain element to a distinct codomain element, what is f?",
            "options": ["Bijective", "Surjective only", "Injective only", "Neither"],
            "answer": "Bijective",
            "exp": "Since a finite map between equal sized sets is one-to-one, it is also onto, hence Bijective."
        }

def solve_ai_math_query(query: str):
    """Processes natural language math questions and routes to the appropriate mathematical engine."""
    query_clean = query.strip().lower()
    response = {
        'query': query,
        'detected_topic': 'General Mathematics',
        'explanation': '',
        'latex': ''
    }

    if any(k in query_clean for k in ['gcd', 'greatest common divisor', 'hcf', 'euclid']):
        nums = [int(x) for x in re.findall(r'\b\d+\b', query)]
        if len(nums) >= 2:
            res = solve_gcd_euclidean(nums[0], nums[1])
            response['detected_topic'] = 'Euclidean GCD'
            response['explanation'] = f"Calculated the Greatest Common Divisor of {nums[0]} and {nums[1]} using the Euclidean Algorithm."
            response['latex'] = res['solution_latex']
            response['result'] = res
            return response

    if any(k in query_clean for k in ['prime', 'factor', 'divisib']):
        nums = [int(x) for x in re.findall(r'\b\d+\b', query)]
        if nums:
            res = solve_divisibility(nums[0])
            response['detected_topic'] = 'Divisibility & Primes'
            response['explanation'] = f"Analyzed integer {nums[0]} for primality, prime factorization, and divisors."
            response['latex'] = res['solution_latex']
            response['result'] = res
            return response

    if any(k in query_clean for k in ['complex', 'argand', 'polar', 'modulus']):
        nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', query)]
        if len(nums) >= 2:
            res = solve_complex_to_polar(nums[0], nums[1])
            response['detected_topic'] = 'Complex Numbers & Polar Form'
            response['explanation'] = f"Converted complex number {nums[0]} + {nums[1]}i to polar form and modulus/argument."
            response['latex'] = res['solution_latex']
            response['result'] = res
            return response

    if any(k in query_clean for k in ['perm', 'comb', 'choose', 'arrangement']):
        nums = [int(x) for x in re.findall(r'\b\d+\b', query)]
        if len(nums) >= 2:
            n, r = max(nums[0], nums[1]), min(nums[0], nums[1])
            if 'comb' in query_clean or 'choose' in query_clean:
                res = solve_combinations(n, r)
                response['detected_topic'] = 'Combinations'
            else:
                res = solve_permutations(n, r)
                response['detected_topic'] = 'Permutations'
            response['explanation'] = f"Computed counting evaluation for n = {n}, r = {r}."
            response['latex'] = res['solution_latex']
            response['result'] = res
            return response

    if any(k in query_clean for k in ['limit', 'continuity']):
        res = solve_limits_continuity('sin(x)/x', 'x', 0)
        response['detected_topic'] = 'Limits & Continuity'
        response['explanation'] = "Here is an example computation for the canonical limit sin(x)/x as x -> 0."
        response['latex'] = res['solution_latex']
        response['result'] = res
        return response

    response['explanation'] = "I am ready to assist with Euclidean Algorithm, Primes & Divisibility, Complex Numbers, De Moivre's Theorem, Permutations & Combinations, Function Mappings, or Limits! Ask me questions like: 'What is the GCD of 1071 and 462?' or 'Convert 3 + 4i to polar form'."
    response['latex'] = r"\gcd(a, b), \quad z = r e^{i\theta}, \quad P(n, r), \quad \binom{n}{r}, \quad \lim_{x \to c} f(x)"
    return response
