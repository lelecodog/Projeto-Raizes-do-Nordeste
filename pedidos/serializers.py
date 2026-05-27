from rest_framework import serializers
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
        fields = ['id_item', 'pedido', 'produto', 'quantidade', 'valor_unitario']


# Pedido
class PedidoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    itens = ItemPedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id_pedido', 'usuario', 'data', 'status', 'canal', 'itens']


# Promocao
class PromocaoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)

    class Meta:
        model = Promocao
        fields = ['id_promocao', 'descricao', 'desconto', 'validade', 'ativo', 'produto']


# Pagamento
class PagamentoSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True)

    class Meta:
        model = Pagamento
        fields = ['id_pagamento', 'pedido', 'valor', 'data', 'status']


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
