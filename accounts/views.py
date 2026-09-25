from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from accounts.serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    # POST /auth/register/ {"username": "", "password": ""}
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
