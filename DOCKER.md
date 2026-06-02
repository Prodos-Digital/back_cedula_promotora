# Docker Compose (backend isolado)

Nesta pasta, o `docker-compose.yml` sobe **PostgreSQL 17** e a **API Django** (Gunicorn na porta 8005).

## Arranque

```bash
cd back_cedula_promotora
cp .env.example .env
# edite .env (senhas, DJANGO_SECRET_KEY, ALLOWED_HOSTS)
docker compose up -d --build
```

Migrações e `collectstatic` correm no `docker-entrypoint.sh` ao iniciar o contentor.

Depois das migrações corre `ensure_bootstrap_superuser`: procura o utilizador com `INIT_SUPERUSER_EMAIL` (por defeito `agencia.prodosdigital@gmail.com`). Se já existir **ativo** como superuser+staff, não altera nada. Senão **cria** esse utilizador ou **promove** um existente com o mesmo e-mail e define `INIT_SUPERUSER_PASSWORD` (por defeito `123senha`). Outros superusers na base não impedem este passo.

## Importar dump SQL no Postgres deste compose

```bash
docker compose exec -T db psql -U cedula -d cedula < dump.sql
```

(Ajuste utilizador e base ao seu `.env`.)

O restore pelo **admin** do Django prefixa o SQL com `DROP SCHEMA IF EXISTS` para schemas auxiliares e, se marcar a opção no formulário (ou `PG_RESTORE_RESET_PUBLIC_SCHEMA=true` no `.env`), **recria o schema `public`** antes do ficheiro — necessário para um `pg_dump` completo de produção aplicar todos os `CREATE TABLE` e `COPY`/`INSERT` quando a base já tinha tabelas do `migrate`.

Scripts em `docker/postgres/initdb/` só correm na **primeira** criação do volume.

## Volume de dados

`postgres_data` persiste entre reinícios. `docker compose down -v` apaga a base.

## Front noutro compose

O projeto Next.js tem o seu próprio `docker-compose` na pasta `web_sistema_emprestimos`. Lá configure `NEXT_INTEGRATION_URL` para apontar para esta API (ex.: `http://127.0.0.1:8005/integration` quando o Next corre na máquina e o backend está publicado na porta 8005). Se usar `host.docker.internal`, o Django precisa desse nome em `ALLOWED_HOSTS` (o `docker-compose` deste backend já inclui por defeito).

## Admin: app Empréstimos (`emp_*`)

As migrações Django deste projeto **não criam** as tabelas `emp_clientes`, `emp_emprestimos`, `emp_acordo_parcelas`, etc. Esses modelos são `managed=False` e correspondem ao schema do **sistema de empréstimos** na base real.

Num Postgres “limpo” (só `migrate`), essas tabelas **não existem** — abrir uma lista no admin (ex.: Acordo parcela) dava erro 500. O admin passa a mostrar uma lista vazia com aviso quando a tabela falta; para ver dados, importe o dump que contenha o schema `emp_*` (e o que precisar de `core_*` / referências), tal como na secção “Importar dump SQL” acima.

## Aviso “core have changes that are not yet reflected in a migration”

É independente do 500 nas abas `emp_*`: o Django detetou diferença entre `integration/core/models.py` e o último estado de migrações. Corrija com `python manage.py makemigrations core` e revê o ficheiro gerado antes de `migrate` em produção (evite renomeações destrutivas de tabelas já existentes no dump).
