# Scripts de inicialização do PostgreSQL

Ficheiros `.sql` ou `.sh` colocados aqui são executados **apenas na primeira criação** do volume de dados (`postgres_data` vazio).

Para **importar um dump numa base já existente**:

```bash
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < o_seu_dump.sql
```

(Execute a partir da pasta `back_cedula_promotora`, com os valores do seu `.env`.)
