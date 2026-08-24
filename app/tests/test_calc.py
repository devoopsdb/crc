from dataclasses import dataclass

from django.test import SimpleTestCase

from app.calc import (
    CalculationError,
    LineResult,
    compute_line,
    reel_count_and_len,
    winding_length,
)


@dataclass
class FakeReel:
    pk: int = 1
    name: str = "R1000"
    diameter: int = 1000
    diameter_neck: int = 500
    length_neck: int = 600
    height: int = 250
    width: int = 600
    mass: int = 120
    max_load: int = 2000


@dataclass
class FakeLine:
    cod: str = "N2XH"
    name: str = "2x2.5"
    con_num: int = 2
    order_len: str = "5000"
    max_len: str = "3000"
    mass: str = "1.52"
    diameter: str = "14.3"


@dataclass
class FakeSettings:
    winding_margin_mm: float = 50.0
    packing_factor: float = 0.93
    bending_radius_multiplier: float = 10.0


@dataclass
class FakeTransport:
    max_load: int = 10000


class WindingLengthTests(SimpleTestCase):
    def test_positive_length(self):
        length = winding_length(FakeReel(), 14.3, 50.0, 0.93)
        self.assertGreater(length, 0)

    def test_zero_diameter_raises(self):
        with self.assertRaises(CalculationError):
            winding_length(FakeReel(), 0, 50.0, 0.93)

    def test_cable_wider_than_barrel_raises(self):
        with self.assertRaises(CalculationError):
            winding_length(FakeReel(), 999, 50.0, 0.93)

    def test_wind_leq_core_raises(self):
        # margin so large that D_wind <= core
        with self.assertRaises(CalculationError):
            winding_length(FakeReel(), 14.3, 1000.0, 0.93)


class ReelCountTests(SimpleTestCase):
    def test_ceil_never_zero(self):
        self.assertEqual(reel_count_and_len(400, 1000), (1, 400.0))

    def test_rounds_up(self):
        count, per_reel = reel_count_and_len(5000, 3000)
        self.assertEqual(count, 2)
        self.assertAlmostEqual(per_reel, 2500.0)

    def test_exact(self):
        self.assertEqual(reel_count_and_len(3000, 1000), (3, 1000.0))

    def test_zero_per_reel_raises(self):
        with self.assertRaises(CalculationError):
            reel_count_and_len(5000, 0)


class ComputeLineTests(SimpleTestCase):
    def test_happy_path(self):
        result = compute_line(FakeLine(), [FakeReel()], FakeSettings(), FakeTransport())
        self.assertIsInstance(result, LineResult)
        self.assertEqual(result.reel_pk, 1)
        self.assertGreaterEqual(result.reel_num, 1)
        self.assertGreater(result.netto_all, 0)
        self.assertAlmostEqual(result.netto_all, 5000 * 1.52, places=2)

    def test_no_reel_fits_raises(self):
        # max_len smaller than any reel's capacity -> no candidates
        line = FakeLine(max_len="1")
        with self.assertRaises(CalculationError):
            compute_line(line, [FakeReel()], FakeSettings(), FakeTransport())

    def test_max_load_warning(self):
        line = FakeLine(order_len="100000", max_len="1000000")
        result = compute_line(
            line, [FakeReel(max_load=1)], FakeSettings(), FakeTransport(max_load=1)
        )
        self.assertIsNotNone(result.warning)
        self.assertIn("load", (result.warning or "").lower())

    def test_bending_radius(self):
        result = compute_line(FakeLine(), [FakeReel()], FakeSettings(), FakeTransport())
        self.assertAlmostEqual(result.bending_radius, 14.3 * 10.0, places=2)

    def test_order_len_non_positive_raises(self):
        line = FakeLine(order_len="0")
        with self.assertRaises(CalculationError):
            compute_line(line, [FakeReel()], FakeSettings(), FakeTransport())

    def test_max_len_non_positive_raises(self):
        line = FakeLine(max_len="0")
        with self.assertRaises(CalculationError):
            compute_line(line, [FakeReel()], FakeSettings(), FakeTransport())

    def test_negative_mass_raises(self):
        line = FakeLine(mass="-1")
        with self.assertRaises(CalculationError):
            compute_line(line, [FakeReel()], FakeSettings(), FakeTransport())