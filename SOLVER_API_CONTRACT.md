# Solver API Contract — Matrix Determinant

**Base URL**: `/api/v1/`  
**Endpoint**: `POST /api/v1/matrix/determinant/`  
**Headers**: `Content-Type: application/json`

---

### Request Payload
```json
{
  "matrix": [
    [1, 2],
    [3, 4]
  ]
}
```

---

### Success Response (`HTTP 200 OK`)
```json
{
  "success": true,
  "solver": "determinant",
  "result": -2,
  "latex": "\\det(A) = -2",
  "steps": [
    {
      "step": 1,
      "title": "State the Matrix",
      "explanation": "Given the 2 × 2 square matrix A:",
      "latex": "A = \\begin{bmatrix} 1 & 2 \\\\ 3 & 4 \\end{bmatrix}"
    },
    {
      "step": 2,
      "title": "Apply 2 × 2 Determinant Formula",
      "explanation": "For any 2 × 2 matrix, the determinant is the difference of the cross-diagonal products: det(A) = ad - bc.",
      "latex": "\\det(A) = (a_{11} \\cdot a_{22}) - (a_{12} \\cdot a_{21})"
    },
    {
      "step": 3,
      "title": "Substitute Values and Evaluate",
      "explanation": "Substitute a11 = 1, a22 = 4, a12 = 2, a21 = 3:",
      "latex": "\\det(A) = (1 \\times 4) - (2 \\times 3) = 4 - (6) = -2"
    },
    {
      "step": 4,
      "title": "Singularity & Invertibility Property",
      "explanation": "If det(A) = 0, the matrix is singular and has no inverse. If det(A) ≠ 0, the matrix is non-singular and invertible.",
      "latex": "\\text{Matrix is } \\mathbf{Invertible (Non-Singular)}"
    }
  ],
  "input": {
    "matrix": [
      [1, 2],
      [3, 4]
    ],
    "dimension": "2x2"
  },
  "details": {
    "is_invertible": true
  }
}
```

---

### Error Response (`HTTP 400 Bad Request`)
```json
{
  "success": false,
  "error": {
    "code": "NON_SQUARE_MATRIX",
    "message": "Matrix must be square (n × n). Provided matrix has dimension 2 × 3."
  }
}
```

### Possible Error Codes
- `EMPTY_BODY`: Request body was empty.
- `MALFORMED_JSON`: Request body was not valid JSON.
- `MISSING_MATRIX_KEY`: Required key `matrix` was missing.
- `EMPTY_MATRIX`: Matrix array is empty or null.
- `RAGGED_MATRIX`: Rows have uneven lengths.
- `NON_SQUARE_MATRIX`: Number of rows does not equal number of columns.
- `NON_NUMERIC_ELEMENT`: Matrix contains non-numeric entries (e.g. strings or empty cells).
- `DIMENSION_OUT_OF_BOUNDS`: Matrix dimension is $< 1\times 1$ or $> 8\times 8$.
