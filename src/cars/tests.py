from django.test import TestCase
from django.urls import reverse

from .models import Car


def make_car(**kwargs):
    data = {
        "car_type": Car.USED,
        "status": Car.AVAILABLE,
        "brand": "Toyota",
        "model_name": "Camry",
        "year": 2020,
        "price": 80000,
        "mileage_km": 50000,
        "city": "الرياض",
    }
    data.update(kwargs)
    return Car.objects.create(**data)


class CarListTests(TestCase):
    def setUp(self):
        self.new_car = make_car(car_type=Car.NEW, model_name="NewModel", mileage_km=None)
        self.new_hidden = make_car(car_type=Car.NEW, model_name="NewHidden", status=Car.HIDDEN)
        self.used_car = make_car(model_name="UsedModel")
        self.used_sold = make_car(model_name="UsedSold", status=Car.SOLD)
        self.used_hidden = make_car(model_name="UsedHidden", status=Car.HIDDEN)

    def test_new_list_shows_only_available_new(self):
        response = self.client.get(reverse("cars:new_list"))
        self.assertEqual(list(response.context["cars"]), [self.new_car])
        self.assertContains(response, reverse("cars:detail", args=[self.new_car.pk]))

    def test_used_list_shows_only_available_used_with_fields(self):
        response = self.client.get(reverse("cars:used_list"))
        self.assertEqual(list(response.context["cars"]), [self.used_car])
        self.assertContains(response, "80000 ريال")
        self.assertContains(response, "2020")
        self.assertContains(response, "50000 كم")
        self.assertContains(response, "الرياض")
        self.assertContains(response, reverse("cars:detail", args=[self.used_car.pk]))

    def test_detail_works_for_available_and_404_for_hidden(self):
        self.assertEqual(self.client.get(reverse("cars:detail", args=[self.used_car.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("cars:detail", args=[self.used_hidden.pk])).status_code, 404)

    def test_home_links_to_list_and_detail_pages(self):
        response = self.client.get(reverse("cars:home"))
        self.assertContains(response, reverse("cars:new_list"))
        self.assertContains(response, reverse("cars:used_list"))
        self.assertContains(response, reverse("cars:detail", args=[self.used_car.pk]))


class CarFilterTests(TestCase):
    def setUp(self):
        self.cheap = make_car(brand="Kia", year=2018, price=40000, city="جدة")
        self.mid = make_car(brand="Toyota", year=2020, price=80000, city="الرياض")
        self.pricey = make_car(brand="Lexus", year=2023, price=200000, city="الرياض")
        self.url = reverse("cars:used_list")

    def results(self, **params):
        return set(self.client.get(self.url, params).context["cars"])

    def test_no_filters_returns_all(self):
        self.assertEqual(self.results(), {self.cheap, self.mid, self.pricey})

    def test_price_range(self):
        self.assertEqual(self.results(price_min=50000, price_max=100000), {self.mid})

    def test_year(self):
        self.assertEqual(self.results(year=2023), {self.pricey})

    def test_city(self):
        self.assertEqual(self.results(city="جدة"), {self.cheap})

    def test_brand(self):
        self.assertEqual(self.results(brand="Toyota"), {self.mid})

    def test_combined_and_invalid_values(self):
        self.assertEqual(self.results(city="الرياض", price_max=100000), {self.mid})
        self.assertEqual(self.results(year="abc", price_min=""), {self.cheap, self.mid, self.pricey})

    def test_reset_link_present(self):
        response = self.client.get(self.url, {"brand": "Kia"})
        self.assertContains(response, f'href="{self.url}"')

    def test_new_list_filters(self):
        new = make_car(car_type=Car.NEW, brand="BMW", year=2025, price=300000)
        make_car(car_type=Car.NEW, brand="Kia", year=2025, price=90000)
        response = self.client.get(reverse("cars:new_list"), {"brand": "BMW"})
        self.assertEqual(list(response.context["cars"]), [new])
