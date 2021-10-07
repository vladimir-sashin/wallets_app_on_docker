from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .documentation_stuff import BAD_REQUEST_RESPONSE
from .serializers import RegisterUserSerializer


class CustomUserCreate(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterUserSerializer,
        responses={201: RegisterUserSerializer, 400: OpenApiTypes.OBJECT},
        examples=[BAD_REQUEST_RESPONSE],
    )
    def create(self, request):
        reg_serializer = RegisterUserSerializer(data=request.data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            if new_user:
                json = reg_serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
