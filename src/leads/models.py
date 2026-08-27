from django.core.exceptions import ValidationError
from django.db import models

from cars.models import Car


class Lead(models.Model):
    TEST_DRIVE = "test_drive"
    VIEWING = "viewing"
    CONTACT = "contact"
    LEAD_TYPE_CHOICES = [
        (TEST_DRIVE, "حجز تجربة قيادة"),
        (VIEWING, "حجز معاينة"),
        (CONTACT, "تواصل عام"),
    ]

    lead_type = models.CharField("نوع الطلب", max_length=20, choices=LEAD_TYPE_CHOICES)
    car = models.ForeignKey(
        Car,
        verbose_name="السيارة",
        related_name="leads",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    name = models.CharField("الاسم", max_length=150)
    phone = models.CharField("رقم الجوال", max_length=30, blank=True)
    email = models.EmailField("البريد الإلكتروني", blank=True)
    preferred_time = models.CharField("الوقت المفضل", max_length=100, blank=True)
    message = models.TextField("الرسالة/الملاحظة", blank=True)

    created_at = models.DateTimeField("تاريخ الطلب", auto_now_add=True)

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_lead_type_display()} - {self.name}"

    def clean(self):
        errors = {}

        if self.lead_type in (self.TEST_DRIVE, self.VIEWING):
            if not self.phone:
                errors["phone"] = "رقم الجوال مطلوب."
            if self.car_id is None:
                errors["car"] = "يجب ربط الطلب بسيارة."
            elif self.lead_type == self.TEST_DRIVE and self.car.car_type != Car.NEW:
                errors["car"] = "حجز تجربة القيادة يكون لسيارة جديدة فقط."
            elif self.lead_type == self.VIEWING and self.car.car_type != Car.USED:
                errors["car"] = "حجز المعاينة يكون لسيارة مستعملة فقط."

        elif self.lead_type == self.CONTACT:
            if not self.phone and not self.email:
                errors["phone"] = "يجب إدخال رقم جوال أو بريد إلكتروني."
            if not self.message:
                errors["message"] = "نص الرسالة مطلوب."

        if errors:
            raise ValidationError(errors)
