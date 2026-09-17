"""
Matrix Determinant Mathematical Service
Computes determinant using symbolic SymPy calculation, providing step-by-step breakdown
for 1x1, 2x2, 3x3, and general nxn matrices.
Decoupled from HTTP, Django, or templates.
"""
try:
    import sympy as sp
except ImportError:
    sp = None

from ..common.validation import validate_matrix, MatrixValidationError
from ..common.response import success_response, error_response

def matrix_to_latex(mat):
    """Converts a 2D array or SymPy Matrix to a standard LaTeX bmatrix."""
    if mat is None:
        return r"\text{N/A}"
    if sp and isinstance(mat, sp.Matrix):
        arr = mat.tolist()
    else:
        arr = mat
    rows_str = []
    for row in arr:
        rows_str.append(" & ".join(str(x) for x in row))
    return r"\begin{bmatrix} " + r" \\ ".join(rows_str) + r" \end{bmatrix}"

def calculate_determinant(raw_matrix):
    """
    Computes determinant with validation and comprehensive step-by-step explanation.
    
    Returns standard dictionary response.
    """
    # 1. Validation
    try:
        matrix, n, cols = validate_matrix(raw_matrix, require_square=True, min_size=1, max_size=8)
    except MatrixValidationError as e:
        return error_response(code=e.code, message=e.message)

    steps = []
    sp_mat = sp.Matrix(matrix) if sp else None

    # Step 1: State Input
    steps.append({
        "step": 1,
        "title": "State the Matrix",
        "explanation": f"Given the {n} × {n} square matrix A:",
        "latex": fr"A = {matrix_to_latex(matrix)}"
    })

    # Step 2: Compute based on dimension
    if n == 1:
        det_val = matrix[0][0]
        steps.append({
            "step": 2,
            "title": "Evaluate 1 × 1 Determinant",
            "explanation": "The determinant of a 1 × 1 matrix is simply its single scalar entry.",
            "latex": fr"\det(A) = {det_val}"
        })
    elif n == 2:
        a = matrix[0][0]
        b = matrix[0][1]
        c = matrix[1][0]
        d = matrix[1][1]
        prod_main = a * d
        prod_anti = b * c
        det_val = prod_main - prod_anti

        steps.append({
            "step": 2,
            "title": "Apply 2 × 2 Determinant Formula",
            "explanation": "For any 2 × 2 matrix, the determinant is the difference of the cross-diagonal products: det(A) = ad - bc.",
            "latex": r"\det(A) = (a_{11} \cdot a_{22}) - (a_{12} \cdot a_{21})"
        })
        steps.append({
            "step": 3,
            "title": "Substitute Values and Evaluate",
            "explanation": f"Substitute a11 = {a}, a22 = {d}, a12 = {b}, a21 = {c}:",
            "latex": fr"\det(A) = ({a} \times {d}) - ({b} \times {c}) = {prod_main} - ({prod_anti}) = {det_val}"
        })
    elif n == 3:
        # 3x3 Laplace Cofactor Expansion along Row 1
        steps.append({
            "step": 2,
            "title": "Apply Laplace Expansion along Row 1",
            "explanation": "Expanding by minors along the first row: det(A) = a11·M11 - a12·M12 + a13·M13.",
            "latex": r"\det(A) = a_{11} \det(M_{11}) - a_{12} \det(M_{12}) + a_{13} \det(M_{13})"
        })

        sub_steps = []
        det_val = 0
        for j in range(3):
            # 2x2 minor formed by removing row 0 and column j
            sub_m = [[matrix[r][c] for c in range(3) if c != j] for r in range(1, 3)]
            minor_det = sub_m[0][0] * sub_m[1][1] - sub_m[0][1] * sub_m[1][0]
            coeff = matrix[0][j]
            sign = (-1)**j
            term = sign * coeff * minor_det
            det_val += term
            sign_str = "+" if sign == 1 else "-"
            sub_steps.append(
                fr"{sign_str} ({coeff}) \cdot \det{matrix_to_latex(sub_m)} = {sign_str} ({coeff}) \cdot ({minor_det}) = {term}"
            )

        steps.append({
            "step": 3,
            "title": "Compute 2 × 2 Minors",
            "explanation": "Calculate each 2 × 2 minor determinant formed by deleting row 1 and column j:",
            "latex": r" \\ ".join(sub_steps)
        })

        steps.append({
            "step": 4,
            "title": "Sum Signed Minor Products",
            "explanation": f"Summing the terms yields the determinant:",
            "latex": fr"\det(A) = {det_val}"
        })
    else:
        # General n x n via Upper Triangular Gaussian Elimination / LU
        if sp:
            sp_mat = sp.Matrix(matrix)
            det_val = int(sp_mat.det()) if sp_mat.det().is_integer else float(sp_mat.det())
        else:
            # Simple recursive determinant fallback
            def _det_recursive(m):
                if len(m) == 1: return m[0][0]
                if len(m) == 2: return m[0][0]*m[1][1] - m[0][1]*m[1][0]
                d = 0
                for c in range(len(m)):
                    sub = [[m[i][j] for j in range(len(m)) if j != c] for i in range(1, len(m))]
                    d += ((-1)**c) * m[0][c] * _det_recursive(sub)
                return d
            det_val = _det_recursive(matrix)
        steps.append({
            "step": 2,
            "title": "Gaussian LU Elimination / Row Operations",
            "explanation": f"For an {n} × {n} matrix, determinant is computed by row-reducing to upper triangular form U and taking the product of the diagonal elements.",
            "latex": r"\det(A) = \prod_{i=1}^n u_{ii}"
        })
        steps.append({
            "step": 3,
            "title": "Exact Evaluated Determinant",
            "explanation": f"Calculated exact determinant for {n} × {n} matrix:",
            "latex": fr"\det(A) = {det_val}"
        })

    # Singularity property
    is_singular = (det_val == 0)
    steps.append({
        "step": len(steps) + 1,
        "title": "Singularity & Invertibility Property",
        "explanation": "If det(A) = 0, the matrix is singular and has no inverse. If det(A) ≠ 0, the matrix is non-singular and invertible.",
        "latex": fr"\text{{Matrix is }} \mathbf{{{ 'Singular (Non-Invertible)' if is_singular else 'Invertible (Non-Singular)' }}}"
    })

    return success_response(
        solver_name="determinant",
        result=det_val,
        latex=fr"\det(A) = {det_val}",
        steps=steps,
        input_data={"matrix": matrix, "dimension": f"{n}x{n}"},
        details={"is_invertible": not is_singular}
    )
