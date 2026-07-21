from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from . import models


@admin.register(models.User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {"fields": ("id", "uuid", "email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "display_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    # "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")
    readonly_fields = ("id", "uuid")

    def user_change_password(self, *args, **kwargs):
        # This seems like a Django bug. Change password view shouldn't choke
        # if we pass extra context (i.e., the current environment) to the view.
        kwargs.pop("extra_context", None)
        return super().user_change_password(*args, **kwargs)


admin.site.index_title = "Index"
admin.site.site_header = f"django-start Administration ({settings.DJANGO_ENV})"
admin.site.site_title = "django-start Administration"
