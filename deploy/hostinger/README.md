# Deploy na VPS Hostinger (Docker + Nginx)

Este guia alinha com o que a Hostinger costuma esperar na VPS: **tráfego público só nas portas 22, 80 e 443**, serviços da aplicação **só em `127.0.0.1`** (evita scans e bloqueios por portas “estranhas” abertas), e **HTTPS** sem domínio usando certificado **autoassinado** (o browser mostra aviso até trocares por Let’s Encrypt quando tiveres DNS).

## Ordem recomendada

1. Na VPS: Docker + Docker Compose plugin + Git + Nginx + OpenSSL.
2. **Backend** (`back_cedula_promotora`): `cp .env.example .env`, editar, `docker compose up -d --build`.
3. **Frontend** (`web_sistema_emprestimos`): idem.
4. **Nginx no host** (terminação TLS): `deploy/hostinger/nginx/vhost-ip-https.conf` (cópia espelhada em `web_sistema_emprestimos/deploy/hostinger/nginx/`).

## 1. Firewall (UFW + painel Hostinger)

No Ubuntu, exemplo:

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

No **hPanel** da Hostinger (Firewall da VPS), confirma que **80** e **443** estão permitidos para entrada.

Não abras **3000** nem **8005** na firewall pública: o `docker-compose.yml` já publica por defeito em **127.0.0.1**; o Nginx fala com essas portas localmente.

## 2. Variáveis de ambiente

Na **raiz deste projeto** (pasta `back_cedula_promotora`, ao lado do `docker-compose.yml`):

```bash
cp .env.example .env
nano .env
```

Pontos críticos em produção atrás de Nginx:

- `ALLOWED_HOSTS` com o **IP público** da VPS (e depois o domínio).
- `BEHIND_HTTPS_PROXY=true` quando o HTTPS termina no Nginx.

## 3. Subir o stack backend

```bash
docker compose up -d --build
```

## 4. HTTPS sem domínio

Gera o certificado **uma vez** no servidor (substitui pelo teu IP):

```bash
sudo bash deploy/hostinger/scripts/gerar-certificado-selfsigned.sh SEU.IP.PUBLICO
```

Configura o Nginx com o ficheiro `deploy/hostinger/nginx/vhost-ip-https.conf` (ajusta caminhos `ssl_certificate` se mudares a pasta). Instruções completas de cópia e `nginx -t` estão no README do frontend, secção Nginx.

## 5. Domínio e HTTPS (Let's Encrypt)

Guia completo com `faturamentocedulapromotora.com.br`, Certbot e ficheiro **`nginx/vhost-faturamentocedulapromotora.com.br.conf`**: ver **`web_sistema_emprestimos/deploy/hostinger/README.md`** (secção 8).

No `.env` deste backend, inclui o hostname em `ALLOWED_HOSTS` e mantém `BEHIND_HTTPS_PROXY=true` atrás do Nginx.

## Ficheiros nesta pasta

| Ficheiro | Função |
|----------|--------|
| `nginx/vhost-ip-https.conf` | Proxy com HTTPS por **IP** (autoassinado) |
| `nginx/vhost-faturamentocedulapromotora.com.br.conf` | Igual ao do frontend — HTTPS **Let's Encrypt** + proxy |
| `scripts/gerar-certificado-selfsigned.sh` | Gera `.crt` / `.key` com SAN=IP |

O `docker-compose.yml` desta pasta mapeia o Gunicorn em **127.0.0.1:8005** por defeito (`${BACKEND_PUBLISH:-127.0.0.1:8005}`; opcional no `.env` — ver `.env.example`).
