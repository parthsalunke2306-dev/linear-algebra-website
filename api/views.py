import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from math_engine.matrix.determinant import calculate_determinant
from math_engine.common.response import error_response

@csrf_exempt
@require_http_methods(["POST"])
def determinant_api_view(request):
    """
    POST /api/v1/matrix/determinant/
    
    Accepts JSON payload:
    {
        "matrix": [[1, 2], [3, 4]]
    }
    
    Returns standard JSON response contract.
    """
    try:
        if not request.body:
            return JsonResponse(
                error_response(code="EMPTY_BODY", message="Request body must be non-empty JSON."),
                status=400
            )

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as json_err:
            return JsonResponse(
                error_response(code="MALFORMED_JSON", message=f"Invalid JSON syntax: {str(json_err)}"),
                status=400
            )

        if not isinstance(data, dict):
            return JsonResponse(
                error_response(code="INVALID_PAYLOAD", message="JSON payload must be an object with a 'matrix' key."),
                status=400
            )

        if "matrix" not in data:
            return JsonResponse(
                error_response(code="MISSING_MATRIX_KEY", message="Missing required key 'matrix' in request payload."),
                status=400
            )

        raw_matrix = data["matrix"]
        result = calculate_determinant(raw_matrix)

        status_code = 200 if result.get("success") else 400
        return JsonResponse(result, status=status_code)

    except Exception as exc:
        return JsonResponse(
            error_response(code="INTERNAL_SERVER_ERROR", message=f"An unexpected error occurred: {str(exc)}"),
            status=500
        )
