# 🏦 Sistema Bancário simples em FastAPI

Um sistema bancário minimalista construído com FastAPI, PostgreSQL e Docker. 

## ✨ Funcionalidades

- 👤 Cadastro de usuários (Pessoa Física e Pessoa Jurídica)
- 🔐 Autenticação JWT segura
- 💸 Transferências entre contas
- 💰 Depósitos e saques para Pessoa Física
- 🏗️ Padrão Repository-Service
- 🧩 Princípios SOLID

## 🚀 Começando

### Pré-requisitos

- 🐳 Docker e Docker Compose

### Configuração

1. Clone este repositório
2. Execute os containers Docker:

```bash
docker-compose up -d
```

3. API disponível em http://localhost:8000
4. Documentação da API: http://localhost:8000/docs

## 🔌 Endpoints da API

### 🔑 Autenticação

#### Registrar Pessoa Física
- **URL:** `POST /api/v1/user/register/natural`
- **Corpo:**
```json
{
  "name": "João Silva",
  "email": "joao@exemplo.com",
  "password": "senha123",
  "address": "Rua das Flores, 123",
  "city": "São Paulo",
  "state": "SP",
  "cpf": "12345678901"
}
```
- **Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1
  },
  "message": "Usuário cadastrado com sucesso"
}
```

#### Registrar Pessoa Jurídica
- **URL:** `POST /api/v1/user/register/legal`
- **Corpo:**
```json
{
  "name": "Empresa ABC LTDA",
  "email": "contato@empresaabc.com",
  "password": "senha456",
  "address": "Avenida Comercial, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "cnpj": "12345678901234"
}
```
- **Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 2
  },
  "message": "Usuário cadastrado com sucesso"
}
```

#### Login
- **URL:** `POST /api/v1/user/login`
- **Corpo:**
```json
{
  "email": "joao@exemplo.com",
  "password": "senha123"
}
```
- **Resposta:**
```json
{
  "success": true,
  "data": [],
  "message": "Login realizado com sucesso"
}
```
> ⚠️ *Um cookie HTTP-only "Authorization" com o token JWT será enviado automaticamente para segurança adicional*

### 💱 Transações (Endpoints protegidos)

#### Transferência entre contas
- **URL:** `POST /api/v1/operation/transfer`
- **Corpo:**
```json
{
  "recipient_id": 2,
  "amount": 500.0
}
```
- **Resposta:**
```json
{
  "success": true,
  "data": {
    "transaction_id": 1,
    "amount": 500.0,
    "new_balance": 500.0
  },
  "message": "Transferência concluída com sucesso"
}
```

#### Depósito (apenas Pessoa Física)
- **URL:** `POST /api/v1/operation/deposit`
- **Corpo:**
```json
{
  "amount": 200.0
}
```
- **Resposta:**
```json
{
  "success": true,
  "data": {
    "transaction_id": 2,
    "amount": 200.0,
    "new_balance": 700.0
  },
  "message": "Depósito realizado com sucesso"
}
```

#### Saque (apenas Pessoa Física)
- **URL:** `POST /api/v1/operation/withdraw`
- **Corpo:**
```json
{
  "amount": 100.0
}
```
- **Resposta:**
```json
{
  "success": true,
  "data": {
    "transaction_id": 3,
    "amount": 100.0,
    "new_balance": 600.0
  },
  "message": "Saque realizado com sucesso"
}
```

## 🗄️ Migrações do Banco de Dados

Comandos úteis para desenvolvimento:

Criar arquivos de migração:
```bash
docker-compose exec api python -m main makemigrations -m "descrição da migração"
```

Aplicar migrações:
```bash
docker-compose exec api python -m main migrate
```

Reverter migrações:
```bash
docker-compose exec api python -m main downgrade
```

Verificar status de migrações:
```bash
docker-compose exec api python -m main show_migrations
```

## 🧪 Executando Testes

Todos os testes:

```bash
docker-compose exec api pytest
```

Testes unitários:

```bash
docker-compose exec api pytest -m unit
```

Testes de integração:

```bash
docker-compose exec api pytest -m integration
```

Relatório de cobertura:

```bash
docker-compose exec api pytest --cov=app
```

---

👨‍💻 Desenvolvido com 💚 por Gabriel
