"""
Matrix validation utilities for mathematical solvers.
Independent of Django, HTTP, and templates.
"""

class MatrixValidationError(Exception):
    """Raised when matrix input fails validation rules."""
    def __init__(self, message, code="INVALID_MATRIX"):
        super().__init__(message)
        self.message = message
        self.code = code

def validate_matrix(matrix, require_square=False, min_size=1, max_size=10):
    """
    Validates a 2D matrix structure.
    
    Checks:
    - Must be a non-empty list of lists.
    - All rows must have identical non-zero lengths.
    - All elements must be convertible to real numbers (int, float, Fraction, or numeric string).
    - If require_square is True, rows count must equal columns count.
    - Dimensions must be between min_size and max_size.
    
    Returns:
    - cleaned_matrix: List of lists of floats or ints.
    - rows: int (row count)
    - cols: int (column count)
    
    Raises:
    - MatrixValidationError if any constraint fails.
    """
    if matrix is None:
        raise MatrixValidationError("Matrix payload cannot be null or empty.", code="EMPTY_MATRIX")

    if not isinstance(matrix, (list, tuple)) or len(matrix) == 0:
        raise MatrixValidationError("Matrix must be a non-empty list of rows.", code="EMPTY_MATRIX")

    rows = len(matrix)
    if rows < min_size or rows > max_size:
        raise MatrixValidationError(
            f"Matrix row count ({rows}) exceeds permitted range [{min_size}, {max_size}].",
            code="DIMENSION_OUT_OF_BOUNDS"
        )

    first_row = matrix[0]
    if not isinstance(first_row, (list, tuple)) or len(first_row) == 0:
        raise MatrixValidationError("First row is invalid or empty.", code="EMPTY_ROW")

    cols = len(first_row)
    if cols < min_size or cols > max_size:
        raise MatrixValidationError(
            f"Matrix column count ({cols}) exceeds permitted range [{min_size}, {max_size}].",
            code="DIMENSION_OUT_OF_BOUNDS"
        )

    cleaned_matrix = []
    for r_idx, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)):
            raise MatrixValidationError(f"Row {r_idx + 1} is not a valid list.", code="INVALID_ROW")
        if len(row) != cols:
            raise MatrixValidationError(
                f"Row {r_idx + 1} has length {len(row)}, expected {cols}. All rows must have equal length.",
                code="RAGGED_MATRIX"
            )

        cleaned_row = []
        for c_idx, val in enumerate(row):
            if val is None or val == "":
                raise MatrixValidationError(
                    f"Element at row {r_idx + 1}, column {c_idx + 1} is blank.",
                    code="EMPTY_ELEMENT"
                )
            try:
                # Handle numeric string, int, float
                f_val = float(val)
                # Keep whole numbers clean
                cleaned_row.append(int(f_val) if f_val.is_integer() else round(f_val, 4))
            except (ValueError, TypeError):
                raise MatrixValidationError(
                    f"Non-numeric value '{val}' at row {r_idx + 1}, column {c_idx + 1}.",
                    code="NON_NUMERIC_ELEMENT"
                )
        cleaned_matrix.append(cleaned_row)

    if require_square and rows != cols:
        raise MatrixValidationError(
            f"Matrix must be square (n × n). Provided matrix has dimension {rows} × {cols}.",
            code="NON_SQUARE_MATRIX"
        )

    return cleaned_matrix, rows, cols
