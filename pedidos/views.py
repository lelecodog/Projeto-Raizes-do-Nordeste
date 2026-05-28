from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Pedido, Usuario, ItemPedido, Produto, Pagamento
from .serializers import PedidoSerializer, PedidoCreateSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()

    def get_serializer_class(self):
        # Usa PedidoCreateSerializer no POST, PedidoSerializer nos demais
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoSerializer

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


