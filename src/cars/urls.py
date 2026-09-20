from django.urls import path

from . import views

app_name = "cars"

urlpatterns = [
    path("", views.home, name="home"),
    path("new/", views.new_list, name="new_list"),
    path("used/", views.used_list, name="used_list"),
]
