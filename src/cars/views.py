from django.shortcuts import render

from .models import Car


def home(request):
    used_cars = Car.objects.filter(
        car_type=Car.USED, status=Car.AVAILABLE
    ).order_by("-created_at")[:6]
    new_cars = Car.objects.filter(
        car_type=Car.NEW, status=Car.AVAILABLE
    ).order_by("-created_at")[:3]
    return render(
        request,
        "cars/home.html",
        {"used_cars": used_cars, "new_cars": new_cars},
    )


def new_list(request):
    return render(request, "cars/new_list.html")


def used_list(request):
    return render(request, "cars/used_list.html")
