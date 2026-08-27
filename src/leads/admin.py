from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "lead_type",
        "name",
        "phone",
        "car",
        "created_at",
    )
    list_filter = ("lead_type",)
    search_fields = ("name", "phone", "email", "car__brand", "car__model_name")
    ordering = ("-created_at",)
