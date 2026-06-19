import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pedidos_api.settings")
django.setup()

from pedidos.models import Usuario, Unidade, Produto, Pedido, ItemPedido, Promocao, Pagamento, Fidelizacao, LogAuditoria
from django.utils import timezone

# Criação do seed para popular o banco de dados com dados iniciais
def run():
    # Usuários
    usuarios = [
        {"nome": "Alex Teste", "email": "alex@teste.com", "perfil": "CLIENTE"},
        {"nome": "Uninter Alex", "email": "uninter@teste.com", "perfil": "CLIENTE"},
        {"nome": "Projeto Alex", "email": "projeto@teste.com", "perfil": "CLIENTE"},
    ]

    usuarios_objs = []

    for u in usuarios:
        usuario = Usuario(
            nome=u["nome"],
            email=u["email"],
            perfil=u["perfil"],
        )
        usuario.set_password("123456")
        usuario.save()
        usuarios_objs.append(usuario)

    # Unidades
    unidades = [
        Unidade(id_unidade=1, nome="Loja Brusque", endereco="Rua Principal, 100", telefone="47 99999-1111", estoque=100),
        Unidade(id_unidade=2, nome="Loja Tijucas", endereco="Av. Central, 200", telefone="48 98888-2222", estoque=100),
        Unidade(id_unidade=3, nome="Loja Nordeste", endereco="Rua das Flores, 300", telefone="81 97777-3333", estoque=100),
    ]
    Unidade.objects.bulk_create(unidades, ignore_conflicts=True)

    # Produtos
    produtos = [
        Produto(id_produto=10, nome="Café Nordestino", categoria="Bebida", preco=12.50, ativo=True, unidade_id=1),
        Produto(id_produto=11, nome="Bolo de Milho", categoria="Doce", preco=20.00, ativo=True, unidade_id=1),
        Produto(id_produto=12, nome="Tapioca Recheada", categoria="Salgado", preco=15.00, ativo=True, unidade_id=2),
    ]
    Produto.objects.bulk_create(produtos, ignore_conflicts=True)

    # Pedidos
    pedido1 = Pedido.objects.create(usuario=usuarios_objs[0], canalPedido="TOTEM")
    pedido2 = Pedido.objects.create(usuario=usuarios_objs[1], canalPedido="APP")
    pedido3 = Pedido.objects.create(usuario=usuarios_objs[2], canalPedido="BALCAO")

    # Itens de pedidos
    ItemPedido.objects.create(pedido=pedido1, produto_id=10, quantidade=2, valor_unitario=12.50)
    ItemPedido.objects.create(pedido=pedido1, produto_id=11, quantidade=1, valor_unitario=20.00)
    ItemPedido.objects.create(pedido=pedido2, produto_id=12, quantidade=1, valor_unitario=15.00)

    # Promoções
    Promocao.objects.create(id_promocao=1, descricao="Promo Café", desconto=2, validade=timezone.now(), ativo=True, produto_id=10)
    Promocao.objects.create(id_promocao=2, descricao="Promo Bolo", desconto=5, validade=timezone.now(), ativo=True, produto_id=11)
    Promocao.objects.create(id_promocao=3, descricao="Promo Tapioca", desconto=5, validade=timezone.now(), ativo=True, produto_id=12)

    # Pagamentos
    Pagamento.objects.create(id_pagamento=1, pedido=pedido1, valor=45.00, data=timezone.now(), status="APROVADO")
    Pagamento.objects.create(id_pagamento=2, pedido=pedido2, valor=15.00, data=timezone.now(), status="APROVADO")
    Pagamento.objects.create(id_pagamento=3, pedido=pedido3, valor=0.00, data=timezone.now(), status="PENDENTE")

    # Fidelização
    Fidelizacao.objects.create(usuario=usuarios_objs[0], saldo_ponto=100, historico="Compra inicial")
    Fidelizacao.objects.create(usuario=usuarios_objs[1], saldo_ponto=50, historico="Promoção aplicada")
    Fidelizacao.objects.create(usuario=usuarios_objs[2], saldo_ponto=0, historico="Cadastro novo")

    # Logs de auditoria
    LogAuditoria.objects.create(id_log=1, pedido=pedido1, acao="CRIACAO", timestamp=timezone.now(), usuario_responsavel="Sistema")
    LogAuditoria.objects.create(id_log=2, pedido=pedido2, acao="PAGAMENTO", timestamp=timezone.now(), usuario_responsavel="Sistema")
    LogAuditoria.objects.create(id_log=3, pedido=pedido3, acao="CANCELAMENTO", timestamp=timezone.now(), usuario_responsavel="Sistema")

    print("Seed concluído com sucesso!")

if __name__ == "__main__":
    run()
