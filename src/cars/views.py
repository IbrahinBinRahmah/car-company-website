from django.shortcuts import get_object_or_404, render

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


def _parse_int(value):
    """يحوّل قيمة الفلتر إلى رقم صحيح موجب، ويتجاهل القيم غير الصالحة."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _filtered_cars(request, car_type):
    """يعيد السيارات المتاحة من النوع المطلوب بعد تطبيق فلاتر GET، مع خيارات القوائم."""
    base_qs = Car.objects.filter(car_type=car_type, status=Car.AVAILABLE)
    cars = base_qs

    brand = request.GET.get("brand", "").strip()
    city = request.GET.get("city", "").strip()
    year = _parse_int(request.GET.get("year"))
    price_min = _parse_int(request.GET.get("price_min"))
    price_max = _parse_int(request.GET.get("price_max"))

    if brand:
        cars = cars.filter(brand=brand)
    if city:
        cars = cars.filter(city=city)
    if year is not None:
        cars = cars.filter(year=year)
    if price_min is not None:
        cars = cars.filter(price__gte=price_min)
    if price_max is not None:
        cars = cars.filter(price__lte=price_max)

    filters = {
        "brand": brand,
        "city": city,
        "year": year,
        "price_min": price_min,
        "price_max": price_max,
    }
    options = {
        "brands": base_qs.order_by("brand").values_list("brand", flat=True).distinct(),
        "cities": base_qs.exclude(city="")
        .order_by("city")
        .values_list("city", flat=True)
        .distinct(),
        "years": base_qs.order_by("-year").values_list("year", flat=True).distinct(),
    }
    is_filtered = any(value not in ("", None) for value in filters.values())

    return {
        "cars": cars.order_by("-created_at"),
        "filters": filters,
        "options": options,
        "is_filtered": is_filtered,
    }


def new_list(request):
    context = _filtered_cars(request, Car.NEW)
    return render(request, "cars/new_list.html", context)


def used_list(request):
    context = _filtered_cars(request, Car.USED)
    return render(request, "cars/used_list.html", context)


def car_detail(request, pk):
    # صفحة مبدئية حتى تنفيذ المهمة 3.7؛ لا تُعرض السيارات المخفية أو المباعة.
    car = get_object_or_404(Car, pk=pk, status=Car.AVAILABLE)
    return render(request, "cars/detail.html", {"car": car})
