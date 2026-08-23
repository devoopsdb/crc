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