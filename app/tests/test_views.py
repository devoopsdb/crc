# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
from django.test import TestCase
from django.urls import reverse

from app.calc import reel_count_and_len, winding_length
from app.models import CableCal, CalculationSettings, ReelsList, TransportList


def make_reel(**kwargs):
    defaults = dict(
        name="R1000", height=250, width=600, diameter=1000,
        diameter_neck=500, length_neck=600, mass=120, max_load=2000,
    )
    defaults.update(kwargs)
    return ReelsList.objects.create(**defaults)


class CableCalViewTests(TestCase):
    def setUp(self):
        CalculationSettings.get_solo()
        self.reel = make_reel()
        self.transport = TransportList.objects.create(
            name="TIR", length=13000, width=2450, height=2700, max_load=24000
        )

    def _post_data(self, lines, order_num="ORD-T1"):
        data = {
            "order_num": order_num,
            "transport": self.transport.pk,
            "form-TOTAL_FORMS": str(len(lines)),
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
        }
        for i, line in enumerate(lines):
            for key, value in line.items():
                data[f"form-{i}-{key}"] = value
        return data

    def test_create_with_one_line(self):
        data = self._post_data([{
            "cod": "X", "name": "N2XH 2x2.5", "con_num": "2",
            "order_len": "5000", "max_len": "3000", "mass": "1.52", "diameter": "14.3",
        }])
        response = self.client.post(reverse("app:cable_cal"), data)
        self.assertEqual(response.status_code, 302)
        calc = CableCal.objects.get(order_num="ORD-T1")
        self.assertEqual(calc.line_items.count(), 1)
        item = calc.line_items.first()
        self.assertIsNotNone(item.reel)
        # reel_num must match the guarded calc module (ceil, never zero).
        capacity = winding_length(self.reel, 14.3, 50.0, 0.93)
        expected_num, _ = reel_count_and_len(5000, capacity)
        self.assertEqual(item.reel_num, expected_num)
        self.assertEqual(float(item.netto_all), round(5000 * 1.52, 2))

    def test_empty_extra_form_is_skipped(self):
        # Two forms: one filled, one empty -> only one line item created.
        data = self._post_data([
            {"cod": "X", "name": "A", "con_num": "2", "order_len": "5000",
             "max_len": "3000", "mass": "1.52", "diameter": "14.3"},
            {},  # empty extra form
        ])
        response = self.client.post(reverse("app:cable_cal"), data)
        self.assertEqual(response.status_code, 302)
        calc = CableCal.objects.get(order_num="ORD-T1")
        self.assertEqual(calc.line_items.count(), 1)

    def test_no_reel_fits_shows_error(self):
        # max_len too small for any reel -> CalculationError, no CableCal saved.
        data = self._post_data([{
            "cod": "X", "name": "big", "con_num": "2",
            "order_len": "10", "max_len": "1", "mass": "1", "diameter": "14.3",
        }])
        response = self.client.post(reverse("app:cable_cal"), data)
        self.assertEqual(response.status_code, 200)  # re-renders with error
        self.assertFalse(CableCal.objects.filter(order_num="ORD-T1").exists())


class CableCalListViewTests(TestCase):
    def setUp(self):
        self.transport = TransportList.objects.create(
            name="TIR", length=13000, width=2450, height=2700, max_load=24000
        )
        self.calc = CableCal.objects.create(order_num="ORD-L1", transport=self.transport)

    def test_list_renders_with_annotated_count(self):
        response = self.client.get(reverse("app:cable_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ORD-L1")
        self.assertEqual(response.context["cable_cal"][0].line_items_count, 0)


class CableCalDetailViewTests(TestCase):
    def setUp(self):
        self.transport = TransportList.objects.create(
            name="TIR", length=13000, width=2450, height=2700, max_load=24000
        )
        self.calc = CableCal.objects.create(order_num="ORD-D1", transport=self.transport)

    def test_detail_renders(self):
        response = self.client.get(reverse("app:cable_detail", kwargs={"pk": self.calc.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ORD-D1")

    def test_delete_view_post_removes_calc(self):
        response = self.client.post(reverse("app:cable_del", kwargs={"pk": self.calc.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CableCal.objects.filter(pk=self.calc.pk).exists())


class ReelsListViewTests(TestCase):
    def setUp(self):
        self.reel = make_reel(name="Reel-Test-1")

    def test_reels_list_renders(self):
        response = self.client.get(reverse("app:reels_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reel-Test-1")

    def test_reels_detail_renders(self):
        response = self.client.get(reverse("app:reels_list_detail", kwargs={"pk": self.reel.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reel-Test-1")

    def test_reels_create(self):
        data = {
            "name": "Reel-New", "height": 250, "width": 600, "diameter": 1200,
            "diameter_neck": 600, "length_neck": 600, "mass": 130, "max_load": 2500,
        }
        response = self.client.post(reverse("app:reels_add"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReelsList.objects.filter(name="Reel-New").exists())

    def test_reels_delete(self):
        response = self.client.post(reverse("app:reels_del", kwargs={"pk": self.reel.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ReelsList.objects.filter(pk=self.reel.pk).exists())


class TransportListViewTests(TestCase):
    def setUp(self):
        self.transport = TransportList.objects.create(
            name="Truck-1", length=10000, width=2400, height=2600, max_load=20000
        )

    def test_transport_list_renders(self):
        response = self.client.get(reverse("app:transport_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Truck-1")

    def test_transport_detail_renders(self):
        response = self.client.get(reverse("app:transport_list_detail", kwargs={"pk": self.transport.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Truck-1")

    def test_transport_create(self):
        data = {
            "name": "Truck-New", "length": 12000, "width": 2450, "height": 2700, "max_load": 22000,
        }
        response = self.client.post(reverse("app:transport_add"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TransportList.objects.filter(name="Truck-New").exists())

    def test_transport_delete(self):
        response = self.client.post(reverse("app:transport_del", kwargs={"pk": self.transport.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TransportList.objects.filter(pk=self.transport.pk).exists())