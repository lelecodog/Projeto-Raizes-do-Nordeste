from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Pedido, Usuario, ItemPedido, Produto, Pagamento
from .serializers import PedidoSerializer, PedidoCreateSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()

    def get_serializer_class(self):
        # Usa PedidoCreateSerializer no POST, PedidoSerializer nos demais
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoSerializer
    
    @swagger_auto_schema(
        request_body=PedidoCreateSerializer,
        responses={201: PedidoSerializer, 400: "Erro de validação"},
        operation_description="Criação de um novo pedido",
        examples={
            "application/json": {
                "clienteId": 123,
                "canalPedido": "APP",
                "formaPagamento": "MOCK",
                "itens": [
                    {"produtoId": 10, "quantidade": 2},
                    {"produtoId": 11, "quantidade": 1}
                ]
            }
        }
    )

    def create(self, request, *args, **kwargs):
        serializer = PedidoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        canalPedido = serializer.validated_data.get("canalPedido")
        clienteId = request.data.get("clienteId")

        try:
            usuario = Usuario.objects.get(id_usuario=clienteId)
        except Usuario.DoesNotExist:
            return Response(
                {"erro": "Cliente não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Criar pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            canalPedido=canalPedido,
            status="AGUARDANDO_PAGAMENTO"
        )

        # Criar itens
        itens = request.data.get("itens", [])
        for item in itens:
            produtoId = item.get("produtoId")
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

        # Mock pagamento
        Pagamento.objects.create(
            pedido=pedido,
            valor=pedido.calcularTotal(),
            status="PENDENTE"
        
        )

        pedido.atualizarStatus("EM_PREPARO")

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
            pedido = Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            return Response({"erro": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        novo_status = request.data.get("status")
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

        if hasattr(pedido, "pagamento") and pedido.pagamento.status == "CONFIRMADO":
            return Response({"erro": "Pedido já pago."}, status=status.HTTP_409_CONFLICT)

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


