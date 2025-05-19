from rest_framework import generics
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
    examples=[
        OpenApiExample(
            name="Example registration request",
            value={
                "username": "string",
                "password": "string",
                "password_confirm": "string",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Example registration response",
            value={"username": "string"},
            response_only=True,
        ),
    ],
)
class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
