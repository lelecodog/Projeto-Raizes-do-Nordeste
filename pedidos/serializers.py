from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    Usuario, Unidade, Produto, ItemPedido,
    Pedido, Promocao, Pagamento, Fidelizacao, LogAuditoria
)

# Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nome', 'email', 'perfil']


# Unidade
class UnidadeSerializer(serializers.ModelSerializer):
    produtos = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Unidade
        fields = ['id_unidade', 'nome', 'endereco', 'telefone', 'estoque', 'produtos']


# Produto
class ProdutoSerializer(serializers.ModelSerializer):
    unidade = serializers.StringRelatedField()

    class Meta:
        model = Produto
        fields = ['id_produto', 'nome', 'categoria', 'preco', 'ativo', 'unidade']


# ItemPedido
class ItemPedidoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)

    class Meta:
        model = ItemPedido
        fields = ['id_item', 'produto', 'quantidade', 'valor_unitario']


# Pedido (resposta completa)
class PedidoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    itens = ItemPedidoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ['id_pedido', 'usuario', 'data', 'status', 'canalPedido', 'itens', 'total']

    def get_total(self, obj):
        return obj.calcularTotal()


# Pedido (entrada para criação)
class ItemPedidoInputSerializer(serializers.Serializer):
    produtoId = serializers.IntegerField()
    quantidade = serializers.IntegerField(default=1)

class PedidoCreateSerializer(serializers.Serializer):
    clienteId = serializers.IntegerField()
    canalPedido = serializers.CharField()
    formaPagamento = serializers.CharField(default="MOCK")
    itens = ItemPedidoInputSerializer(many=True)

    def validate_clienteId(self, value):
        if not Usuario.objects.filter(id_usuario=value).exists():
            raise serializers.ValidationError("Cliente não encontrado.")
        return value


# Promocao
class PromocaoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)

    class Meta:
        model = Promocao
        fields = ['id_promocao', 'descricao', 'desconto', 'validade', 'ativo', 'produto']


# Pagamento
class PagamentoSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Pagamento
        fields = ['id_pagamento', 'pedido', 'valor', 'data', 'status', 'total']

    def get_total(self, obj):
        return obj.pedido.calcularTotal()


# Fidelizacao
class FidelizacaoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Fidelizacao
        fields = ['id_fidelizacao', 'usuario', 'saldo_ponto', 'historico']


# LogAuditoria
class LogAuditoriaSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True)

    class Meta:
        model = LogAuditoria
        fields = ['id_log', 'pedido', 'acao', 'timestamp', 'usuario_responsavel']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # autentica usando email
        user = authenticate(request=self.context.get("request"), email=email, password=password)
        if not user:
            raise serializers.ValidationError("Credenciais inválidas")
        data["user"] = user
        return data