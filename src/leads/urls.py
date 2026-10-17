from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("contact/", views.contact, name="contact"),
]
