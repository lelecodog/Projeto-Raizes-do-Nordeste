from django.contrib import admin
from .models import Usuario, Unidade, Produto, ItemPedido, Pedido, Promocao, Pagamento, Fidelizacao, LogAuditoria


admin.site.register(Usuario)
admin.site.register(Unidade)
admin.site.register(Produto)
admin.site.register(ItemPedido)
admin.site.register(Pedido)
admin.site.register(Promocao)
admin.site.register(Pagamento)
admin.site.register(Fidelizacao)
admin.site.register(LogAuditoria)
