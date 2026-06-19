from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from pedidos.models import Usuario
from pedidos.serializers import LoginSerializer
from drf_yasg.utils import swagger_auto_schema

class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(usuario)
        refresh.set_exp(lifetime=timedelta(days=7))

        access = refresh.access_token
        access.set_exp(lifetime=timedelta(minutes=30))

        return Response({
            "refresh": str(refresh),
            "access": str(access),
        }, status=status.HTTP_200_OK)

