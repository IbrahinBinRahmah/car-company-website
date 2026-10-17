from django.test import TestCase
from django.urls import reverse

from .models import Lead


class StaticPagesTests(TestCase):
    def test_pages_load(self):
        for name in ("leads:contact", "about", "privacy"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_contact_page_shows_contact_info_and_map(self):
        response = self.client.get(reverse("leads:contact"))
        self.assertContains(response, "tel:")
        self.assertContains(response, "mailto:")
        self.assertContains(response, "google.com/maps")
        self.assertContains(response, "<form", html=False)

    def test_pages_linked_in_navigation_and_footer(self):
        response = self.client.get(reverse("cars:home"))
        self.assertContains(response, f'href="{reverse("leads:contact")}"')
        self.assertContains(response, f'href="{reverse("about")}"')
        self.assertContains(response, f'href="{reverse("privacy")}"')


class ContactFormTests(TestCase):
    url = reverse("leads:contact")

    def test_valid_submission_creates_contact_lead(self):
        response = self.client.post(
            self.url,
            {"name": "أحمد", "phone": "0500000000", "message": "استفسار عن التمويل"},
            follow=True,
        )
        self.assertContains(response, "تم استلام رسالتك بنجاح")
        lead = Lead.objects.get()
        self.assertEqual(lead.lead_type, Lead.CONTACT)
        self.assertIsNone(lead.car)
        self.assertEqual(lead.message, "استفسار عن التمويل")

    def test_email_alone_is_enough(self):
        self.client.post(
            self.url, {"name": "سارة", "email": "sara@example.com", "message": "مرحبا"}
        )
        self.assertEqual(Lead.objects.count(), 1)

    def test_rejected_without_phone_or_email(self):
        response = self.client.post(self.url, {"name": "أحمد", "message": "مرحبا"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "يجب إدخال رقم جوال أو بريد إلكتروني.")
        self.assertFalse(Lead.objects.exists())

    def test_rejected_without_message(self):
        response = self.client.post(self.url, {"name": "أحمد", "phone": "0500000000"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["message"])
        self.assertFalse(Lead.objects.exists())
