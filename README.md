## Sistema Backend da Cédula Promotora e Sistema de empréstimos pessoais do Sr. Felipe

Esse sistema de backend é utilizado pelo sistema de controle financeiro da Cédula Promotora e o Sistema de controle de empréstimos pessoais do Sr. Felipe.

```bash
  pasta/app: /integration/core          #módulo da cédula promotora
  pasta/app: /integration/emprestimos   #módulo dos sistema de empréstimos
  pasta/app: /integration/auth          #módulo de auth compartilhado entre as duas aplicações
```

## Variáveis de Ambiente

Para rodar esse projeto, você vai precisar adicionar as seguintes variáveis de ambiente no seu .env

`DB_NAME`

`DB_USER`

`DB_PASSWORD`

`DB_HOST`

`DATABASE_URL`

`DB_PORT`

### Backup no admin (PostgreSQL)

O `pg_dump` / `psql` do PATH têm de ser da **mesma major** (ou mais nova) que o servidor. Se o RDS for PG 17 e o Homebrew tiver só o cliente 14, instale o 17 e aponte no `.env`:

`PG_DUMP_BIN` — caminho absoluto para `pg_dump` (ex.: `/opt/homebrew/opt/postgresql@17/bin/pg_dump`)

`PSQL_BIN` — caminho absoluto para `psql` (ex.: `/opt/homebrew/opt/postgresql@17/bin/psql`)

No Apple Silicon o prefixo costuma ser `/opt/homebrew/opt/...`; no Intel, `/usr/local/opt/...`.

## Rodando localmente

Para rodar o projeto localmente:

```bash
  python3 -m venv ven #Criar o ambiente virtual

  source venv/bin/activate #NO AMBIENTE LINUX
  venv/Scripts/activate #NO AMBIENTE WINDOWS

  python3 manage.py runserver 127.0.0.1:8005
```

## Docker (Postgres + API nesta pasta)

```bash
cp .env.example .env
docker compose up -d --build
```

Ver `DOCKER.md` e `.env.example` (variáveis `POSTGRES_*`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, etc.).

## Autor

- [@glaysonvisgueira](https://www.github.com/glaysonvisgueira)
