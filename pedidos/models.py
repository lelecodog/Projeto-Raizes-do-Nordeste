from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# Usuario (com perfis: cliente, atendente, gerente, admin)
class Usuario(models.Model):
    PERFIS = [
        ("CLIENTE", "Cliente"),
        ("ATENDENTE", "Atendente"),
        ("GERENTE", "Gerente"),
        ("ADMIN", "Admin"),
    ]

    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha_hash = models.CharField(max_length=255)
    perfil = models.CharField(max_length=20, choices=PERFIS, default="CLIENTE")

    def criarConta(self, senha):
        self.senha_hash = make_password(senha)
        self.save()
        return self

    def autenticar(self, senha):
        return check_password(senha, self.senha_hash)

    def atualizarPerfil(self, novoNome=None, novoEmail=None):
        if novoNome:
            self.nome = novoNome
        if novoEmail:
            self.email = novoEmail
        self.save()

    def consultarPedidos(self):
        return self.pedidos.all()

    def __str__(self):
        return f"{self.nome} ({self.perfil})"


# Unidade
class Unidade(models.Model):
    id_unidade = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20)
    estoque = models.IntegerField(default=0)

    def gerarEstoque(self):
        return self.estoque

    def listarProduto(self):
        return self.produtos.all()

    def __str__(self):
        return self.nome


# Produto
class Produto(models.Model):
    id_produto = models.AutoField(primary_key=True)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name="produtos")
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def aplicarPromocao(self, promocao):
        if promocao.validarValidade():
            self.preco -= promocao.desconto
            self.save()

    def verificarDisponibilidade(self):
        return self.ativo and self.unidade.estoque > 0

    def __str__(self):
        return self.nome


# ItemPedido
class ItemPedido(models.Model):
    id_item = models.AutoField(primary_key=True)
    pedido = models.ForeignKey("Pedido", on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def calcularSubtotal(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return f"Item {self.produto.nome} (x{self.quantidade})"


# Pedido
class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="pedidos")
    data = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, default="AGUARDANDO_PAGAMENTO")
    canalPedido = models.CharField(max_length=20)

    def adicionarItem(self, item):
        item.pedido = self
        item.save()

    def calcularTotal(self):
        return sum([item.calcularSubtotal() for item in self.itens.all()])

    def atualizarStatus(self, novoStatus):
        self.status = novoStatus
        self.save()

    def cancelar(self):
        self.status = "CANCELADO"
        self.save()

    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.usuario.nome}"


# Promocao
class Promocao(models.Model):
    id_promocao = models.AutoField(primary_key=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="promocoes")
    descricao = models.CharField(max_length=200)
    desconto = models.DecimalField(max_digits=5, decimal_places=2)
    validade = models.DateField()
    ativo = models.BooleanField(default=True)

    def aplicarEmProduto(self, produto):
        if self.validarValidade():
            produto.aplicarPromocao(self)

    def aplicarEmPedido(self, pedido):
        if self.validarValidade():
            for item in pedido.itens.all():
                item.valor_unitario -= self.desconto
                item.save()

    def validarValidade(self):
        return self.ativo and self.validade >= timezone.now().date()

    def __str__(self):
        return f"Promoção {self.descricao}"


# Pagamento
class Pagamento(models.Model):
    id_pagamento = models.AutoField(primary_key=True)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="pagamento")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="PENDENTE")

    def processarPagamento(self):
        # Simulação de processamento
        self.status = "PROCESSANDO"
        self.save()
        return True

    def confirmarPagamento(self):
        self.status = "CONFIRMADO"
        self.save()
        self.pedido.atualizarStatus("EM_PREPARO")

    def registrarFalha(self, motivo):
        self.status = f"FALHA: {motivo}"
        self.save()

    def __str__(self):
        return f"Pagamento {self.id_pagamento} - {self.status}"


# Fidelizacao
class Fidelizacao(models.Model):
    id_fidelizacao = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="fidelizacao")
    saldo_ponto = models.IntegerField(default=0)
    historico = models.TextField(blank=True)

    def acumularPontos(self, valorPedido):
        pontos = int(valorPedido // 10)  # exemplo: 1 ponto a cada 10 reais
        self.saldo_ponto += pontos
        self.save()

    def resgatarPontos(self, qtdPontos):
        if qtdPontos <= self.saldo_ponto:
            self.saldo_ponto -= qtdPontos
            self.save()
            return True
        return False

    def __str__(self):
        return f"Fidelização de {self.usuario.nome}"


# LogAuditoria
class LogAuditoria(models.Model):
    id_log = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="logs")
    acao = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    usuario_responsavel = models.CharField(max_length=100)

    def registrarAcao(self, acao, usuario):
        self.acao = acao
        self.usuario_responsavel = usuario
        self.save()

    def __str__(self):
        return f"Log {self.id_log} - {self.acao}"



