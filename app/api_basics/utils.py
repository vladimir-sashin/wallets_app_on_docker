from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission


class UserWalletPermission(BasePermission):
    """Permission that restricts 'retrieve' action of 'wallets' resource - it won't return a wallet that is not owned
    by current user and raise 403 in this case."""

    def has_object_permission(self, request, view, obj):
        return obj.holder == request.user


class WalletsPagination(PageNumberPagination):
    """Pagination class for 'list' action of 'wallets' resource."""

    page_size = 5
    page_query_param = "page_size"
    max_page_size = 100


class TransactionsPagination(PageNumberPagination):
    """Pagination class for 'history' action of 'wallets' resource."""

    page_size = 50
    page_query_param = "page_size"
    max_page_size = 100
