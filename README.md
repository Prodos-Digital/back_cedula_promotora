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

## Rodando localmente

Para rodar o projeto localmente:

```bash
  python3 -m venv ven #Criar o ambiente virtual

  source venv/bin/activate #NO AMBIENTE LINUX
  venv/Scripts/activate #NO AMBIENTE WINDOWS

  python3 manage.py runserver 127.0.0.1:8005
```

## Autor

- [@glaysonvisgueira](https://www.github.com/glaysonvisgueira)
