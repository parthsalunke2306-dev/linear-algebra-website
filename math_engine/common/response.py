"""
Standard API response builders for all mathematical solvers.
Guarantees consistent contract across all endpoints.
"""

def success_response(solver_name, result, latex, steps=None, details=None, input_data=None):
    """
    Builds a standardized success payload.
    """
    response = {
        "success": True,
        "solver": solver_name,
        "result": result,
        "latex": latex,
        "steps": steps or []
    }
    if input_data is not None:
        response["input"] = input_data
    if details is not None:
        response["details"] = details
    return response

def error_response(code, message, details=None):
    """
    Builds a standardized error payload.
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if details is not None:
        response["error"]["details"] = details
    return response
