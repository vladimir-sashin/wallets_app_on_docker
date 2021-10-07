from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Switch from CSVRenderer to JSONRenderer for exceptions"""
    if context["request"].accepted_renderer.format == "csv":
        context["request"].accepted_renderer = JSONRenderer()
    return exception_handler(exc, context)


@api_view()
def error_404_page(request, exception=None):
    """View to return default 404 error response in JSON instead of HTML by default."""
    return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


# validation error messages
TRANSACTION_AMOUNT_ZERO_NEGATIVE_ERROR = "Negative or zero value"
INSUFFICIENT_FUNDS_ERROR = "Insufficient funds"
RECIPIENT_IS_SENDER_ERROR = "Recipient cannot be sender"
RECIPIENT_DOESNT_EXIST_ERROR = "Recipient with provided id doesn't exist"
DATERANGE_BEFORE_AFTER_ERROR = "timestamp_before' is less then start date"
