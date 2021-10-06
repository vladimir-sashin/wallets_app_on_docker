from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import exception_handler


class InsufficientFunds(ParseError):
    """Exception that indicates that sender doesn't have enough funds to make requested transfer."""

    default_detail = _("InsufficientFunds")


def custom_exception_handler(exc, context):
    """Switch from CSVRenderer to JSONRenderer for exceptions"""
    if context["request"].accepted_renderer.format == "csv":
        context["request"].accepted_renderer = JSONRenderer()
    return exception_handler(exc, context)


@api_view()
def error_404_page(request, exception=None):
    """View to return default 404 error response in JSON instead of HTML by default."""
    return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
