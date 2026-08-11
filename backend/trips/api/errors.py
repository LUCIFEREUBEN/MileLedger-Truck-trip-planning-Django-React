from rest_framework.views import exception_handler


def structured_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    field_errors = response.data if isinstance(response.data, dict) else {}
    response.data = {
        "code": "invalid_input" if response.status_code == 400 else "request_failed",
        "message": "Review the highlighted fields."
        if response.status_code == 400
        else "The request could not be completed.",
        "field_errors": field_errors,
        "retryable": response.status_code >= 500,
    }
    return response
