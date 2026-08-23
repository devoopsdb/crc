# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from app.models import CableCal, CableLineItem, CalculationSettings, ReelsList, TransportList


class CalculationSettingsTests(TestCase):
    def test_solo_creates_one_row(self):
        a = CalculationSettings.get_solo()
        b = CalculationSettings.get_solo()
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(CalculationSettings.objects.count(), 1)
        self.assertEqual(a.packing_factor, 0.93)
        self.assertEqual(a.winding_margin_mm, 50.0)


class CableLineItemTests(TestCase):
    def setUp(self):
        self.transport = TransportList.objects.create(
            name="TIR", length=13000, width=2450, height=2700, max_load=24000
        )
        self.calc = CableCal.objects.create(order_num="ORD-1", transport=self.transport)

    def test_create_line_item(self):
        item = CableLineItem.objects.create(
            cable_cal=self.calc,
            position=0,
            cod="X",
            name="N2XH 2x2.5",
            order_len="5000",
            max_len="3000",
            mass="1.52",
            diameter="14.3",
        )
        self.assertEqual(str(item), "N2XH 2x2.5 (X)")
        self.assertEqual(self.calc.line_items.count(), 1)


class ReelsListConstraintTests(TestCase):
    def _bad_reel(self, **overrides):
        defaults = dict(
            name="bad", height=100, width=100, diameter=100,
            diameter_neck=200, length_neck=100, mass=10, max_load=100,
        )
        defaults.update(overrides)
        return ReelsList(**defaults)

    def test_diameter_must_exceed_neck(self):
        reel = self._bad_reel()  # diameter 100 <= neck 200
        with self.assertRaises((ValidationError, IntegrityError)):
            reel.full_clean()
            with transaction.atomic():  # type: ignore
                reel.save()

    def test_max_load_positive(self):
        reel = self._bad_reel(diameter=300, diameter_neck=100, max_load=0)
        with self.assertRaises((ValidationError, IntegrityError)):
            reel.full_clean()
            with transaction.atomic():  # type: ignore
                reel.save()

    def test_valid_reel_saves(self):
        reel = ReelsList(
            name="ok", height=250, width=600, diameter=1000,
            diameter_neck=500, length_neck=600, mass=120, max_load=2000,
        )
        reel.full_clean()  # should not raise
        reel.save()
        self.assertIsNotNone(reel.pk)