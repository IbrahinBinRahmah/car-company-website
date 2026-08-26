from django.core.exceptions import ValidationError
from django.db import models


class Branch(models.Model):
    """فرع/معرض تابع للشركة."""

    name = models.CharField("الاسم", max_length=150)
    city = models.CharField("المدينة", max_length=100)
    address = models.CharField("العنوان", max_length=255, blank=True)
    phone = models.CharField("رقم الهاتف", max_length=30, blank=True)
    whatsapp = models.CharField("واتساب", max_length=30, blank=True)
    email = models.EmailField("البريد الإلكتروني", blank=True)

    class Meta:
        verbose_name = "فرع"
        verbose_name_plural = "الفروع"

    def __str__(self):
        return f"{self.name} - {self.city}"


class Car(models.Model):
    NEW = "NEW"
    USED = "USED"
    CAR_TYPE_CHOICES = [
        (NEW, "جديد"),
        (USED, "مستعمل"),
    ]

    AVAILABLE = "available"
    HIDDEN = "hidden"
    SOLD = "sold"
    STATUS_CHOICES = [
        (AVAILABLE, "متاحة"),
        (HIDDEN, "مخفية"),
        (SOLD, "مباعة"),
    ]

    TRANSMISSION_AUTOMATIC = "automatic"
    TRANSMISSION_MANUAL = "manual"
    TRANSMISSION_CHOICES = [
        (TRANSMISSION_AUTOMATIC, "أوتوماتيك"),
        (TRANSMISSION_MANUAL, "يدوي"),
    ]

    FUEL_PETROL = "petrol"
    FUEL_DIESEL = "diesel"
    FUEL_HYBRID = "hybrid"
    FUEL_ELECTRIC = "electric"
    FUEL_TYPE_CHOICES = [
        (FUEL_PETROL, "بنزين"),
        (FUEL_DIESEL, "ديزل"),
        (FUEL_HYBRID, "هايبرد"),
        (FUEL_ELECTRIC, "كهربائي"),
    ]

    SPEC_SAUDI = "saudi"
    SPEC_GULF = "gulf"
    SPEC_IMPORTED = "imported"
    SPEC_ORIGIN_CHOICES = [
        (SPEC_SAUDI, "سعودي"),
        (SPEC_GULF, "خليجي"),
        (SPEC_IMPORTED, "مستورد"),
    ]

    car_type = models.CharField("نوع السيارة", max_length=4, choices=CAR_TYPE_CHOICES)
    status = models.CharField(
        "حالة السيارة", max_length=10, choices=STATUS_CHOICES, default=AVAILABLE
    )

    brand = models.CharField("الماركة", max_length=100)
    model_name = models.CharField("الموديل", max_length=100)
    trim = models.CharField("الفئة", max_length=100, blank=True)
    year = models.PositiveIntegerField("السنة")

    price = models.DecimalField(
        "السعر", max_digits=10, decimal_places=2, null=True, blank=True
    )
    mileage_km = models.PositiveIntegerField("الممشى (كم)", null=True, blank=True)

    transmission = models.CharField(
        "ناقل الحركة", max_length=20, choices=TRANSMISSION_CHOICES, blank=True
    )
    fuel_type = models.CharField(
        "نوع الوقود", max_length=20, choices=FUEL_TYPE_CHOICES, blank=True
    )
    engine_size = models.CharField("سعة المحرك", max_length=50, blank=True)
    exterior_color = models.CharField("اللون الخارجي", max_length=50, blank=True)

    branch = models.ForeignKey(
        Branch,
        verbose_name="المدينة/الفرع",
        related_name="cars",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    specification_origin = models.CharField(
        "الوارد/المواصفات", max_length=20, choices=SPEC_ORIGIN_CHOICES, blank=True
    )

    short_description = models.TextField("وصف مختصر", blank=True)

    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "سيارة"
        verbose_name_plural = "السيارات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.model_name} {self.year}"

    def clean(self):
        if self.car_type == self.USED:
            errors = {}
            if self.price is None:
                errors["price"] = "السعر مطلوب للسيارات المستعملة."
            if self.mileage_km is None:
                errors["mileage_km"] = "الممشى مطلوب للسيارات المستعملة."
            if errors:
                raise ValidationError(errors)


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField("الصورة", upload_to="cars/%Y/%m/")
    is_primary = models.BooleanField("صورة رئيسية", default=False)
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "صورة سيارة"
        verbose_name_plural = "صور السيارات"
        ordering = ["order", "id"]

    def __str__(self):
        return f"صورة {self.car} ({'رئيسية' if self.is_primary else self.order})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            CarImage.objects.filter(car=self.car).exclude(pk=self.pk).update(
                is_primary=False
            )
