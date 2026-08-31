from rest_framework.views import exception_handler


class BusinessError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def api_exception_handler(exc, context):
    from rest_framework.response import Response
    from rest_framework import status

    if isinstance(exc, BusinessError):
        return Response(
            {"code": exc.code, "message": exc.message, "details": exc.details},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "code": getattr(exc, "default_code", "API_ERROR"),
            "message": response.data,
            "details": {},
        }
    return response
