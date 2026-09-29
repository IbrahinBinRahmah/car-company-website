from django.urls import path

from . import views

app_name = "cars"

urlpatterns = [
    path("", views.home, name="home"),
    path("new/", views.new_list, name="new_list"),
    path("used/", views.used_list, name="used_list"),
    path("new/<int:pk>/", views.new_detail, name="new_detail"),
    path("used/<int:pk>/", views.used_detail, name="used_detail"),
]
