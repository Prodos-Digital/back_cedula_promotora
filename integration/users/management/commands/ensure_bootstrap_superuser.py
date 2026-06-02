"""
Garante o superutilizador inicial definido por e-mail (arranque Docker, etc.).

Regra:
- Procura o utilizador com o e-mail de bootstrap (INIT_SUPERUSER_EMAIL ou defeito).
- Se já existir, estiver ativo e for superuser + staff → não altera nada.
- Caso contrário → cria o utilizador ou promove o existente e define a senha
  (INIT_SUPERUSER_PASSWORD ou defeito), sistema_origem e roles.

Não depende de “haver ou não outro superuser” na base: só importa este e-mail.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rolepermissions.roles import assign_role

User = get_user_model()

DEFAULT_EMAIL = "agencia.prodosdigital@gmail.com"
DEFAULT_PASSWORD = "123senha"


def _username_from_email(email: str) -> str:
    local = email.split("@", 1)[0]
    base = local.replace(".", "_").replace("+", "_")[:200]
    if not base:
        base = "admin"
    candidate = base
    n = 0
    while User.objects.filter(username=candidate).exclude(email__iexact=email).exists():
        n += 1
        candidate = f"{base}_{n}"
    return candidate


class Command(BaseCommand):
    help = (
        "Garante o superutilizador com INIT_SUPERUSER_EMAIL (ou defeito): "
        "se já existir ativo como superuser, ignora; senão cria ou promove."
    )

    def handle(self, *args, **options):
        email = (os.environ.get("INIT_SUPERUSER_EMAIL") or DEFAULT_EMAIL).strip().lower()
        password = os.environ.get("INIT_SUPERUSER_PASSWORD", DEFAULT_PASSWORD)

        if not email:
            self.stderr.write(
                self.style.ERROR(
                    "ensure_bootstrap_superuser: e-mail de bootstrap vazio; defina INIT_SUPERUSER_EMAIL."
                )
            )
            return

        user = User.objects.filter(email__iexact=email).first()

        if user and user.is_superuser and user.is_staff and user.is_active:
            self.stdout.write(
                self.style.NOTICE(
                    f"ensure_bootstrap_superuser: {email} já existe como superutilizador ativo; "
                    "nada a fazer."
                )
            )
            return

        if user:
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.sistema_origem = user.sistema_origem or "emprestimo"
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.WARNING(
                    f"ensure_bootstrap_superuser: {email} promovido a superutilizador "
                    "(senha e flags atualizadas)."
                )
            )
        else:
            username = _username_from_email(email)
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            user.is_active = True
            user.sistema_origem = "emprestimo"
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"ensure_bootstrap_superuser: criado superutilizador {email} "
                    f"(username={username})."
                )
            )

        try:
            assign_role(user, "app_permissions")
            assign_role(user, "menu_permissions")
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"ensure_bootstrap_superuser: roles não atribuídas ({exc})."
                )
            )
