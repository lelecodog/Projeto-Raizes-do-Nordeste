from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from pedidos.models import Usuario

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        senha = request.data.get("password")

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Verifica senha corretamente
        if not usuario.check_password(senha):
            return Response({"detail": "Senha incorreta"}, status=status.HTTP_400_BAD_REQUEST)

        # Criar token manualmente usando id_usuario
        refresh = RefreshToken.for_user(usuario)
        refresh.set_exp(lifetime=timedelta(days=7))

        access = refresh.access_token
        access.set_exp(lifetime=timedelta(minutes=30))

        return Response({
            "refresh": str(refresh),
            "access": str(access),
        }, status=status.HTTP_200_OK)

