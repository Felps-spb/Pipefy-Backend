# Pipefy Backend

Backend em FastAPI para criacao de clientes, persistencia local e simulacao de integracao com cards do Pipefy via GraphQL.

## Requisitos

- Python 3.13
- uv
- Docker

## Configuracao

Crie um arquivo `.env` na raiz do projeto:

```env
PSQL_HOST=localhost
PSQL_DB=app_db
PSQL_USER=postgres
PSQL_PASSWORD=postgres
PSQL_PORT=5432

PIPEFY_PIPE_ID=PIPE_ID_SIMULADO
PIPEFY_FIELD_CLIENTE_NOME=cliente_nome
PIPEFY_FIELD_CLIENTE_EMAIL=cliente_email
PIPEFY_FIELD_VALOR_PATRIMONIO=valor_patrimonio
PIPEFY_FIELD_STATUS=status
PIPEFY_FIELD_PRIORIDADE=prioridade
```

## Execucao Local

Usando Makefile:

```bash
make setup
make db-up
make run
```

Ou execute os comandos manualmente:

Crie o ambiente virtual:

```bash
uv venv
```

Instale as dependencias:

```bash
uv sync
```

Suba o PostgreSQL:

```bash
docker compose up -d postgres
```

Inicie a API:

```bash
uv run uvicorn app.main:app --reload --reload-dir app --reload-exclude ".pytest_cache/*" --reload-exclude ".venv/*"
```

A documentacao interativa fica em:

```text
http://127.0.0.1:8000/docs
```

## Testes

As dependencias de teste sao instaladas pelo `uv sync`.

Execute:

```bash
make test
```

Ou manualmente:

```bash
uv run pytest
```

Os testes cobrem criacao de cliente, regra de prioridade no webhook e bloqueio de `event_id` duplicado.

## Criar Cliente

Endpoint:

```text
POST /clientes
```

Exemplo:

```bash
curl -X POST "http://127.0.0.1:8000/clientes/" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "Joao Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualizacao cadastral",
    "valor_patrimonio": 250000
  }'
```

A API salva o cliente localmente com status inicial `Aguardando Analise`, calcula a prioridade e retorna tambem o payload GraphQL simulado de criacao do card no Pipefy.

## Webhook Pipefy

Endpoint:

```text
POST /webhooks/pipefy/card-updated
```

Exemplo:

```bash
curl -X POST "http://127.0.0.1:8000/webhooks/pipefy/card-updated" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

A API verifica idempotencia pelo `event_id`, busca o cliente pelo e-mail, recalcula a prioridade, marca o status como `Processado` e retorna o payload GraphQL simulado para atualizar campos do card no Pipefy.

Se o mesmo `event_id` for enviado novamente, a resposta vem com `already_processed: true` e o evento nao e processado de novo.

## Visao de Producao na AWS

A aplicação é toda desenvolvida utilizando conceitos de Clean Architecture e DDD. Isso ajuda bastante na escalabilidade horizontal do projeto, mantendo um equilíbrio entre complexidade e capacidade de expansão.

Em um ambiente de produção, os endpoints poderiam ser expostos via API Gateway, enquanto a aplicação seria executada em Lambda, ECS Fargate ou App Runner. Para workloads com baixo ou médio volume de webhooks, API Gateway + Lambda oferece menor custo operacional e escalabilidade automática. Em cenários com maior demanda, o ECS permitiria o uso de Load Balancer e políticas de auto scaling para ajuste dinâmico da quantidade de tarefas conforme a carga da aplicação. 

Os clientes poderiam ficar em RDS PostgreSQL quando houver necessidade de consultas relacionais, integridade transacional e SQL. A tabela de idempotencia dos webhooks poderia ficar no mesmo RDS ou em DynamoDB, usando `event_id` como chave primaria com escrita condicional para bloquear duplicidade com baixa latencia.

Para maior resiliencia, o endpoint de webhook poderia gravar o evento em SQS e responder rapidamente ao Pipefy. Um worker Lambda ou ECS consumiria a fila, aplicaria a regra de negocio, atualizaria o banco e chamaria a API do Pipefy. Isso desacopla recebimento e processamento, permite retry controlado e evita perda de eventos em picos.
