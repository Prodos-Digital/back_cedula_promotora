"""
Ferramentas de backup/restore expostas no Django Admin (somente superusuário).

PostgreSQL: pg_dump / psql (clientes no PATH).
SQLite: dump textual via `sqlite3 <ficheiro> .dump`; restore com `sqlite3` a ler o SQL.
O download usa extensão .sql (conteúdo SQL do banco a que o Django está ligado).
"""
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods


def _require_superuser(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise PermissionDenied


def _pg_env():
    db = settings.DATABASES["default"]
    env = os.environ.copy()
    if db.get("PASSWORD"):
        env["PGPASSWORD"] = str(db["PASSWORD"])
    host = str(db.get("HOST") or "")
    if "PGSSLMODE" not in os.environ:
        if "amazonaws.com" in host or "rds.amazonaws.com" in host:
            env["PGSSLMODE"] = "require"
        else:
            env.setdefault("PGSSLMODE", "prefer")
    return env


def _is_postgres():
    return settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def _is_sqlite():
    return settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"


def _dump_filename():
    name = str(settings.DATABASES["default"].get("NAME") or "database")
    stem = Path(name).stem if name else "database"
    return f"dump_{stem}.sql"


def _remove_sqlite_files(path: Path):
    """Remove ficheiro principal e sidecars WAL/SHM."""
    for p in (
        path,
        path.parent / f"{path.name}-wal",
        path.parent / f"{path.name}-shm",
    ):
        try:
            p.unlink(missing_ok=True)
        except OSError:
            pass


_SCHEMA_NAME_OK = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*\Z")


def _pg_schema_ident_quoted(name: str):
    """Nome de schema seguro para interpolar em SQL (aspas duplas). None se inválido."""
    n = (name or "").strip()
    if not n or not _SCHEMA_NAME_OK.match(n):
        return None
    return '"' + n.replace('"', '""') + '"'


def _pg_restore_drop_schema_lines():
    """DROP SCHEMA IF EXISTS … CASCADE por schema conhecido + PG_RESTORE_PREAMBLE_EXTRA_SCHEMAS."""
    builtin = ("_heroku", "heroku_ext", "rede-gov", "tst")
    extra = getattr(settings, "PG_RESTORE_PREAMBLE_EXTRA_SCHEMAS", ()) or ()
    seen = set()
    lines = []
    for raw in (*builtin, *extra):
        ident = _pg_schema_ident_quoted(raw)
        if not ident:
            continue
        key = raw.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"DROP SCHEMA IF EXISTS {ident} CASCADE;")
    return lines


def _pg_restore_preamble_sql(*, use_reset_public: bool) -> bytes:
    """
    SQL executado antes do dump importado (plain SQL).

    1) DROP de schemas auxiliares (Heroku, rede-gov, tst, …) para evitar
       "schema … already exists".
    2) Opcionalmente repõe o schema public (DROP … CASCADE + CREATE): necessário
       para um pg_dump completo de produção recriar todas as tabelas e aplicar todos
       os COPY/INSERT quando a base local já tinha tabelas do ``migrate``.
    """
    parts = [
        "-- Preamble: preparar re-importação de dump completo (produção → dev)",
        "SET client_min_messages TO WARNING;",
        *_pg_restore_drop_schema_lines(),
    ]
    if use_reset_public:
        parts.extend(
            [
                "",
                "-- Repor schema public: evita 'relation … already exists' e permite",
                "-- que o dump crie tabelas e insira TODOS os dados (COPY/INSERT).",
                "DROP SCHEMA IF EXISTS public CASCADE;",
                "CREATE SCHEMA public;",
                "GRANT ALL ON SCHEMA public TO CURRENT_USER;",
                "GRANT USAGE ON SCHEMA public TO PUBLIC;",
            ]
        )
    parts.append("")
    return "\n".join(parts).encode("utf-8")


def _pg_restore_use_reset_public(request) -> bool:
    """Checkbox no POST ou PG_RESTORE_RESET_PUBLIC_SCHEMA no .env."""
    if request.POST.get("reset_public") == "1":
        return True
    return bool(getattr(settings, "PG_RESTORE_RESET_PUBLIC_SCHEMA", False))


def _pg_tool_hint(stderr: str) -> str:
    if "version mismatch" not in stderr.lower():
        return ""
    return (
        "\n\n---\nDica: o pg_dump/psql local tem de ser da mesma major (ou mais recente) "
        "que o PostgreSQL do servidor. Ex.: Homebrew:\n"
        "  brew install postgresql@17\n"
        "No .env defina (ajuste o prefixo se for Intel Mac /usr/local):\n"
        "  PG_DUMP_BIN=/opt/homebrew/opt/postgresql@17/bin/pg_dump\n"
        "  PSQL_BIN=/opt/homebrew/opt/postgresql@17/bin/psql\n"
    )


@require_GET
def admin_database_dump(request):
    _require_superuser(request)

    if _is_postgres():
        db = settings.DATABASES["default"]
        cmd = [
            settings.PG_DUMP_BIN,
            "-h",
            str(db.get("HOST") or "localhost"),
            "-p",
            str(db.get("PORT") or "5432"),
            "-U",
            str(db["USER"]),
            "-d",
            str(db["NAME"]),
            "--no-owner",
            "--no-acl",
            "-F",
            "p",
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            env=_pg_env(),
            timeout=3600,
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="replace") or "pg_dump falhou"
            err = err + _pg_tool_hint(err)
            return HttpResponse(err, status=500, content_type="text/plain; charset=utf-8")
        body = proc.stdout
        filename = _dump_filename()
        resp = HttpResponse(body, content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    if _is_sqlite():
        name = settings.DATABASES["default"]["NAME"]
        path = Path(name).resolve()
        if not path.is_file():
            return HttpResponse("Ficheiro SQLite não encontrado.", status=404)
        proc = subprocess.run(
            ["sqlite3", str(path), ".dump"],
            capture_output=True,
            timeout=3600,
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="replace") or "sqlite3 .dump falhou"
            return HttpResponse(err, status=500, content_type="text/plain; charset=utf-8")
        body = proc.stdout
        filename = _dump_filename()
        resp = HttpResponse(body, content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    return HttpResponse(
        "Engine de banco não suportado para dump automático.",
        status=400,
        content_type="text/plain; charset=utf-8",
    )


@require_http_methods(["GET", "POST"])
def admin_database_restore(request):
    _require_superuser(request)

    if request.method == "GET":
        return render(
            request,
            "admin/db_restore.html",
            {
                "title": "Importar dump do banco",
                "is_postgres": _is_postgres(),
                "is_sqlite": _is_sqlite(),
                "pg_restore_reset_public_env": getattr(
                    settings, "PG_RESTORE_RESET_PUBLIC_SCHEMA", False
                ),
            },
        )

    # POST
    confirm = request.POST.get("confirm") == "1"
    if not confirm:
        messages.error(request, "Marque a confirmação para prosseguir.")
        return redirect("admin_db_restore")

    upload = request.FILES.get("dump_file")
    if not upload:
        messages.error(request, "Envie o arquivo de dump.")
        return redirect("admin_db_restore")

    if _is_postgres():
        db = settings.DATABASES["default"]
        use_reset_public = _pg_restore_use_reset_public(request)
        suffix = Path(upload.name).suffix.lower() or ".sql"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(_pg_restore_preamble_sql(use_reset_public=use_reset_public))
            for chunk in upload.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            connections.close_all()
            cmd = [
                settings.PSQL_BIN,
                "-h",
                str(db.get("HOST") or "localhost"),
                "-p",
                str(db.get("PORT") or "5432"),
                "-U",
                str(db["USER"]),
                "-d",
                str(db["NAME"]),
                "-v",
                "ON_ERROR_STOP=1",
                "-f",
                tmp_path,
            ]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                env=_pg_env(),
                timeout=7200,
            )
            if proc.returncode != 0:
                err = proc.stderr.decode("utf-8", errors="replace") or proc.stdout.decode(
                    "utf-8", errors="replace"
                )
                err = err + _pg_tool_hint(err)
                hint = ""
                if (
                    "already exists" in err
                    and not use_reset_public
                    and ("relation" in err.lower() or "schema" in err.lower())
                ):
                    hint = (
                        "\n\n---\nSe este dump é um pg_dump completo de produção e a base já tinha "
                        "tabelas (migrate), marque no formulário «Repor schema public antes do import» "
                        "ou defina PG_RESTORE_RESET_PUBLIC_SCHEMA=true no .env."
                    )
                messages.error(request, f"psql retornou erro:\n{(err + hint)[:4500]}")
                return redirect("admin_db_restore")
            if use_reset_public:
                messages.success(
                    request,
                    "Restore concluído: o schema public foi reposto e o dump aplicou a estrutura "
                    "e os dados em sequência. Confirme no Postgres (contagens / amostras). "
                    "Reinicie o Gunicorn se a app ficar com erros de ligação em cache.",
                )
            else:
                messages.success(
                    request,
                    "Restore concluído. Verifique o banco; em caso de erro parcial, use backup recente.",
                )
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return redirect("admin:index")

    if _is_sqlite():
        name = settings.DATABASES["default"]["NAME"]
        path = Path(name).resolve()
        backup = path.with_suffix(path.suffix + ".bak-admin")
        suffix = Path(upload.name).suffix.lower() or ".sql"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="wb") as tmp:
            for chunk in upload.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            connections.close_all()
            if path.exists():
                shutil.copy2(path, backup)
                _remove_sqlite_files(path)
            with open(tmp_path, "rb") as dump_in:
                proc = subprocess.run(
                    ["sqlite3", str(path)],
                    stdin=dump_in,
                    capture_output=True,
                    timeout=7200,
                )
            if proc.returncode != 0:
                err = proc.stderr.decode("utf-8", errors="replace") or proc.stdout.decode(
                    "utf-8", errors="replace"
                )
                # tentar repor backup se existir
                if backup.exists() and not path.exists():
                    try:
                        shutil.copy2(backup, path)
                    except OSError:
                        pass
                messages.error(request, f"sqlite3 retornou erro:\n{err[:4000]}")
                return redirect("admin_db_restore")
            messages.success(
                request,
                f"Restore SQL aplicado. Cópia do ficheiro anterior: {backup.name}. "
                "Reinicie o runserver se notar erros de ligação.",
            )
        except Exception as exc:
            messages.error(request, str(exc))
            return redirect("admin_db_restore")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return redirect("admin:index")

    messages.error(request, "Engine de banco não suportado para restore automático.")
    return redirect("admin:index")
