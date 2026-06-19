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
- SECRET_KEY=chave_super_secreta
- DEBUG=True
- DATABASE_URL=sqlite:///db.sqlite3

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
- [docs/API_Pedidos.postman_collection.json](Docs/API_Pedidos.postman_collection.json)

### Importação
- No Postman: vá em *Collections* → *Import* → selecione o arquivo `.json`.
- No Insomnia: vá em *Application Menu* → *Import Data* → *From File* → selecione o `.json`.

O token JWT obtido no login deve ser usado em todas as requisições (exceto nos cenários de erro sem token).

### Ordem sugerida de execução (Fluxo A)

1. **[T01 - Login](ca://s?q=T01_Login)**  
   - `POST /auth/login/`  
   - Obter token JWT para autenticação.

2. **[T02 - Criar Pedido](ca://s?q=T02_Criar_Pedido)**  
   - `POST /pedidos/`  
   - Criar pedido com itens válidos.

3. **[T03 - Consultar Pedidos](ca://s?q=T03_Consultar_Pedidos)**  
   - `GET /pedidos/`  
   - Listar pedidos do usuário autenticado.

4. **[T04 - Consultar sem Token](ca://s?q=T04_Acesso_sem_Token)** *(Erro)*  
   - `GET /pedidos/` sem `Authorization`.  
   - Esperado: `401 Unauthorized`.

5. **[T05 - Simular Pagamento](ca://s?q=T05_Simular_Pagamento)**  
   - `POST /pedidos/simular_pagamento/`  
   - Confirmar pagamento mock.

6. **[T06 - Atualizar Status](ca://s?q=T06_Atualizar_Status)**  
   - `PATCH /pedidos/{id}/atualizar_status/`  
   - Alterar status para `EM_PREPARO`, `FINALIZADO` ou `CANCELADO`.

7. **[T07 - Criar Pedido com Cliente Inexistente](ca://s?q=T07_Criar_Pedido_com_Cliente_Inexistente)** *(Erro)*  
   - `POST /pedidos/` com `clienteId` inválido.  
   - Esperado: `400 Bad Request`.

8. **[T08 - Criar Pedido com Produto Inexistente](ca://s?q=T08_Produto_inexistente_no_pedido)** *(Erro)*  
   - `POST /pedidos/` com `produtoId` inválido.  
   - Esperado: `400 Bad Request`.

9. **[T09 - Simular Pagamento já efetuado](ca://s?q=T09_Simular_pagamento_ja_efetuado)** *(Erro)*  
   - `POST /pedidos/simular_pagamento/` em pedido já pago.  
   - Esperado: `409 Conflict`.

10. **[T10 - Consultar Pedido sem Token](ca://s?q=T10_Consultar_Pedido_sem_Token)** *(Erro)*  
    - `GET /pedidos/{id}/` sem `Authorization`.  
    - Esperado: `401 Unauthorized`.

### Evidências
- Prints da execução dos testes estão disponíveis em `docs/evidencias.pdf`.
- Cada pasta (Auth, Produtos, Pedidos, Pagamento, Erros) contém os cenários positivos e negativos.

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

O sistema não coleta dados sensíveis como CPF, dados financeiros ou endereço completo, limitando-se a informações essenciais para execução do contrato.

## 10. Finalizando

Este projeto cumpre os requisitos mínimos da disciplina, entregando uma API funcional, documentada e testável. O Fluxo A foi implementado com persistência em banco, autenticação JWT e documentação técnica completa, simulando um cenário real de mercado.