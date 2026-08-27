from django.contrib import admin

from .models import Car, CarImage


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ("image", "is_primary", "order")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "brand",
        "model_name",
        "year",
        "car_type",
        "status",
        "price",
        "mileage_km",
        "city",
        "created_at",
    )
    list_filter = ("car_type", "status", "city", "specification_origin", "transmission", "fuel_type")
    search_fields = ("brand", "model_name", "trim", "city")
    ordering = ("-created_at",)
    inlines = [CarImageInline]

    fieldsets = (
        ("النوع والحالة", {"fields": ("car_type", "status")}),
        ("بيانات أساسية", {"fields": ("brand", "model_name", "trim", "year")}),
        (
            "بيانات السيارة المستعملة",
            {
                "fields": ("price", "mileage_km"),
                "description": "السعر والممشى إلزاميان للسيارات المستعملة.",
            },
        ),
        (
            "مواصفات فنية",
            {
                "fields": (
                    "transmission",
                    "fuel_type",
                    "engine_size",
                    "exterior_color",
                )
            },
        ),
        ("الموقع والمواصفات", {"fields": ("city", "specification_origin")}),
        ("الوصف", {"fields": ("short_description",)}),
    )


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ("car", "is_primary", "order")
    list_filter = ("is_primary",)
    search_fields = ("car__brand", "car__model_name")
    ordering = ("car", "order")
