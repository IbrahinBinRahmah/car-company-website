import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Car, CarImage

# صورة GIF صغيرة (1x1) لاختبار معرض الصور
TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


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
        self.assertContains(response, self.new_car.get_absolute_url())

    def test_used_list_shows_only_available_used_with_fields(self):
        response = self.client.get(reverse("cars:used_list"))
        self.assertEqual(list(response.context["cars"]), [self.used_car])
        self.assertContains(response, "80000 ريال")
        self.assertContains(response, "2020")
        self.assertContains(response, "50000 كم")
        self.assertContains(response, "الرياض")
        self.assertContains(response, self.used_car.get_absolute_url())


    def test_home_links_to_list_and_detail_pages(self):
        response = self.client.get(reverse("cars:home"))
        self.assertContains(response, reverse("cars:new_list"))
        self.assertContains(response, reverse("cars:used_list"))
        self.assertContains(response, self.used_car.get_absolute_url())
        self.assertContains(response, self.new_car.get_absolute_url())


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


TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class CarDetailTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.used = make_car(
            transmission=Car.TRANSMISSION_AUTOMATIC,
            fuel_type=Car.FUEL_PETROL,
            engine_size="2.5L",
            exterior_color="أبيض",
            specification_origin=Car.SPEC_SAUDI,
            short_description="السيارة بحالة ممتازة",
        )
        self.new = make_car(car_type=Car.NEW, brand="BMW", model_name="X5", year=2025, price=300000, mileage_km=None)

    def add_images(self, car, count):
        for i in range(count):
            CarImage.objects.create(
                car=car, order=i, image=SimpleUploadedFile(f"img{i}.gif", TINY_GIF, content_type="image/gif")
            )

    def test_urls_are_split_by_type(self):
        self.assertEqual(self.used.get_absolute_url(), reverse("cars:used_detail", args=[self.used.pk]))
        self.assertEqual(self.new.get_absolute_url(), reverse("cars:new_detail", args=[self.new.pk]))
        # لا يمكن فتح سيارة عبر مسار النوع الآخر
        self.assertEqual(self.client.get(reverse("cars:new_detail", args=[self.used.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("cars:used_detail", args=[self.new.pk])).status_code, 404)

    def test_hidden_and_sold_return_404(self):
        hidden = make_car(status=Car.HIDDEN)
        sold = make_car(car_type=Car.NEW, status=Car.SOLD)
        self.assertEqual(self.client.get(hidden.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(sold.get_absolute_url()).status_code, 404)

    def test_used_detail_shows_price_specs_description_and_viewing(self):
        response = self.client.get(self.used.get_absolute_url())
        self.assertTemplateUsed(response, "cars/used_detail.html")
        for text in [
            "Toyota Camry", "80000 ريال", "50000 كم", "2020", "أوتوماتيك", "بنزين",
            "2.5L", "أبيض", "الرياض", "سعودي", "السيارة بحالة ممتازة", "حجز معاينة",
        ]:
            self.assertContains(response, text)
        self.assertNotContains(response, "حجز تجربة قيادة")

    def test_new_detail_shows_starting_price_specs_and_test_drive(self):
        response = self.client.get(self.new.get_absolute_url())
        self.assertTemplateUsed(response, "cars/new_detail.html")
        self.assertContains(response, "BMW X5")
        self.assertContains(response, "ابتداءً من")
        self.assertContains(response, "300000 ريال")
        self.assertContains(response, "مواصفات مختصرة")
        self.assertContains(response, "حجز تجربة قيادة")
        self.assertNotContains(response, "حجز معاينة")

    def test_new_detail_without_price(self):
        self.new.price = None
        self.new.save()
        response = self.client.get(self.new.get_absolute_url())
        self.assertContains(response, "السعر عند الطلب")
        self.assertNotContains(response, "ابتداءً من")

    def test_gallery_shows_all_images(self):
        self.add_images(self.used, 3)
        response = self.client.get(self.used.get_absolute_url())
        self.assertContains(response, 'id="carGallery"')
        self.assertContains(response, "carousel-item", count=3)
        self.assertContains(response, 'data-bs-slide-to="2"')
        for img in self.used.images.all():
            self.assertContains(response, img.image.url)

    def test_gallery_placeholder_without_images(self):
        response = self.client.get(self.new.get_absolute_url())
        self.assertContains(response, "لا توجد صور لهذه السيارة")
