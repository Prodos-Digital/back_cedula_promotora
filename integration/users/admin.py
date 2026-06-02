from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "username")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """ModelAdmin + formulários auth: evita campos inexistentes do UserAdmin stock (first_name, etc.)."""

    form = UserAdminForm
    add_form = CustomUserCreationForm
    ordering = ("email",)
    list_display = (
        "id",
        "email",
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
        "sistema_origem",
        "created",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "username")
    readonly_fields = ("last_login", "created", "updated")
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Permissões"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Sistema"), {"fields": ("sistema_origem",)}),
        (_("Datas"), {"fields": ("created", "updated", "last_login")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()
