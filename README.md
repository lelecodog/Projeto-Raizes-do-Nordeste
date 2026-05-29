# Sistema de Pedidos – Fluxo A

## 📌 Descrição do Projeto
Este projeto implementa o **Fluxo A** de um sistema de pedidos para uma rede de unidades.  
O fluxo contempla:

- Criação de pedidos com validação de itens e regras básicas.  
- Registro de pagamento mock (simulado).  
- Atualização de status do pedido (AGUARDANDO_PAGAMENTO → EM_PREPARO → PRONTO → ENTREGUE ou CANCELADO).  

O objetivo é demonstrar um **MVP funcional** com persistência em banco de dados (SQLite), documentação via Swagger/OpenAPI e testes organizados em Postman/Insomnia.  
Outros recursos (autenticação JWT, fidelidade, estoque, unidade, promoções) foram **documentados** mas não implementados, conforme permitido pela especificação. Por tanto
esta implementação visa demostrar apenas o funcionamento do fluxo de pedidos.


## 1. Requisitos
- **Linguagem**: Python 3.13  
- **Framework**: Django 6.0.5  
- **Banco de dados**: SQLite (default do Django)  
- **Dependências principais**:
  - Django==6.0.5  
  - djangorestframework==3.17.1  
  - drf-yasg==1.21.15 (Swagger/OpenAPI)  
  - PyYAML==6.0.3  

## 2. Configuração de variáveis de ambiente
Crie um arquivo `.env` baseado no exemplo abaixo (`.env.example`):

env
SECRET_KEY=chave_super_secreta
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

- cp .env.example .env

## 3. Instalação de dependências
Ative seu ambiente virtual e instale os pacotes:

- pip install -r requirements.txt

## 4. Banco de dados
Crie as tabelas e rode o seed inicial:

- python manage.py migrate
- python seed.py

O script seed.py insere dados iniciais no banco para facilitar os testes:

- Usuários: id_usuario=123, id_usuario=124 e id_usuario=125
- Unidade: id_unidade=1, id_unidade=2 e id_unidade=3
- Produtos: id_produto=10, id_produto=11 e id_produto=12
- + 3 registros de Pedido, ItemPedido, Promocao, Pagamento, Fidelizacao e LogAuditoria

## 5. Iniciar a API

- python manage.py runserver

A API estará disponível em:

http://127.0.0.1:8000/

## 6. Documentação (Swagger/OpenAPI)
Acesse a documentação interativa em:

http://127.0.0.1:8000/swagger/
ou
http://127.0.0.1:8000/redoc/


## 7. Testes (Postman/Insomnia)

A coleção de testes está disponível em:
- [docs/API_Pedidos.postman_collection.json](docs/API_Pedidos.postman_collection.json)

Ordem sugerida:

Login (mock) → obter token.

Criar pedido (POST /pedidos).

Consultar pedido (GET /pedidos/{id}).

Atualizar status (PATCH /pedidos/{id}/status).

Simular pagamento (POST /pagamentos).

Cenários de erro (ex.: produto inexistente, canalPedido inválido).

## 8. Fluxo obrigatório (Fluxo A)

O sistema implementa o fluxo completo:

Criar pedido.

Validar itens e regras básicas.

Registrar pagamento mock.

Atualizar status do pedido.

## 9. LGPD e Segurança
Dados coletados: nome, email, telefone, perfil.

Finalidade: cadastro de cliente e execução de pedidos.

Base legal: execução de contrato.

Controles: autenticação JWT (documentada), perfis de acesso, hashing de senha, logs de auditoria (não implementados, apenas descritos).