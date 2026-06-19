from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Pedido, Usuario, ItemPedido, Produto, Pagamento
from .serializers import PedidoSerializer, PedidoCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoSerializer
    
    @swagger_auto_schema(
        request_body=PedidoCreateSerializer,
        responses={201: PedidoSerializer, 400: "Erro de validação"},
        operation_description="Criação de um novo pedido"
    )
    def create(self, request, *args, **kwargs):
        serializer = PedidoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        canalPedido = serializer.validated_data["canalPedido"]
        clienteId = serializer.validated_data["clienteId"]

        try:
            usuario = Usuario.objects.get(id_usuario=clienteId)
        except Usuario.DoesNotExist:
            return Response(
                {"erro": "Cliente não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        pedido = Pedido.objects.create(
            usuario=usuario,
            canalPedido=canalPedido,
            status="AGUARDANDO_PAGAMENTO"
        )

        # Criar itens
        itens = serializer.validated_data.get("itens", [])
        for item in itens:
            produtoId = item["produtoId"]
            quantidade = item.get("quantidade", 1)
            try:
                produto = Produto.objects.get(id_produto=produtoId)
            except Produto.DoesNotExist:
                return Response(
                    {"erro": f"Produto {produtoId} não encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                valor_unitario=produto.preco
            )

        # Pagamento inicial pendente
        Pagamento.objects.create(
            pedido=pedido,
            valor=pedido.calcularTotal(),
            status="PENDENTE"
        )

        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        method='patch',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="EM_PREPARO"
                )
            }
        ),
        responses={200: PedidoSerializer, 404: "Pedido não encontrado"},
        operation_description="Atualização do status de um pedido"
    )
    @action(detail=True, methods=['patch'])
    def atualizar_status(self, request, pk=None):
        try:
            pedido = Pedido.objects.get(pk=pk, usuario=request.user)
        except Pedido.DoesNotExist:
            return Response({"erro": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        novo_status = request.data.get("status")
        if not novo_status:
            return Response({"erro": "Campo 'status' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        if novo_status not in ["EM_PREPARO", "FINALIZADO", "CANCELADO"]:
            return Response({"erro": "Status inválido."}, status=status.HTTP_400_BAD_REQUEST)

        pedido.atualizarStatus(novo_status)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'pedidoId': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'formaPagamento': openapi.Schema(type=openapi.TYPE_STRING, example="MOCK")
            }
        ),
        responses={201: "Pagamento confirmado", 409: "Pedido já pago"},
        operation_description="Simulação de pagamento mock"
    )
    @action(detail=False, methods=['post'])
    def simular_pagamento(self, request):
        pedidoId = request.data.get("pedidoId")
        formaPagamento = request.data.get("formaPagamento", "MOCK")

        try:
            pedido = Pedido.objects.get(id_pedido=pedidoId)
        except Pedido.DoesNotExist:
            return Response({"erro": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        pagamento = getattr(pedido, "pagamento", None)
        if pagamento and pagamento.status == "CONFIRMADO":
            return Response({"erro": "Pedido já pago."}, status=status.HTTP_409_CONFLICT)

        if pagamento:
            pagamento.status = "CONFIRMADO"
            pagamento.save()
        else:
            pagamento = Pagamento.objects.create(
                pedido=pedido,
                valor=pedido.calcularTotal(),
                status="CONFIRMADO"
            )

        pedido.atualizarStatus("PAGO")
        return Response({
            "id_pagamento": pagamento.id_pagamento,
            "pedido": pedido.id_pedido,
            "valor": pagamento.valor,
            "status": pagamento.status
        }, status=status.HTTP_201_CREATED)

