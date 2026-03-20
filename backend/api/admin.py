from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Case, Client, Coverage, Damages, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "is_staff", "is_superuser", "is_active")
    search_fields = ("email",)
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    readonly_fields = ("last_login",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_superuser", "is_active"),
            },
        ),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "liable")
    search_fields = ("name", "email", "phone")


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "client", "status", "recommendation", "created_at")
    list_filter = ("status", "recommendation")
    search_fields = ("incident_type", "incident_summary", "voice_note_url")


@admin.register(Damages)
class DamagesAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "treatment_received", "treatment_type", "treatment_cost")
    list_filter = ("treatment_received",)


@admin.register(Coverage)
class CoverageAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "type", "policy_limit", "deductible", "insurer_name")
    list_filter = ("type",)
