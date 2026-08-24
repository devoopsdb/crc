# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportIncompatibleMethodOverride=false
from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CalculationSettings(models.Model):
    winding_margin_mm = models.FloatField(
        default=50.0,
        verbose_name=_("Winding margin (mm)"),
        help_text=_("Unwound margin per flange side."),
    )
    packing_factor = models.FloatField(
        default=0.93,
        verbose_name=_("Packing factor"),
    )
    bending_radius_multiplier = models.FloatField(
        default=10.0,
        verbose_name=_("Bending radius multiplier (x cable diameter)"),
    )
    use_flange_height = models.BooleanField(
        default=False,
        verbose_name=_("Use flange height to bound winding"),
    )

    class Meta:
        verbose_name = _("Calculation settings")
        verbose_name_plural = _("Calculation settings")

    @classmethod
    def get_solo(cls) -> "CalculationSettings":
        obj, created = cls.objects.get_or_create(pk=1, defaults={"pk": 1})
        return obj

    def __str__(self):
        return str(_("Calculation settings"))


class CableCal(models.Model):
    order_num = models.CharField(
        max_length=50, unique=True, db_index=True, verbose_name=_("Order number")
    )
    transport = models.ForeignKey(
        "TransportList",
        null=True,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name=_("Transport"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    # Per-calculation overrides of the global CalculationSettings defaults.
    margin_override = models.FloatField(
        null=True, blank=True, verbose_name=_("Winding margin override (mm)")
    )
    packing_override = models.FloatField(
        null=True, blank=True, verbose_name=_("Packing factor override")
    )

    def get_absolute_url(self):
        return reverse("app:cable_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.order_num)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-created_at"]


class ReelsList(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Reel name"))
    height = models.IntegerField(verbose_name=_("Flange height (mm)"))
    width = models.IntegerField(verbose_name=_("Width (mm)"))
    diameter = models.IntegerField(verbose_name=_("Diameter (mm)"))
    diameter_neck = models.IntegerField(verbose_name=_("Core diameter (mm)"))
    length_neck = models.IntegerField(verbose_name=_("Barrel width (mm)"))
    max_load = models.IntegerField(verbose_name=_("Max load (kg)"))
    mass = models.IntegerField(verbose_name=_("Reel mass (kg)"))
    reel_type = models.ForeignKey(
        "ReelType",
        verbose_name=_("Reel type"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def get_absolute_url(self):
        return reverse("app:reels_list_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _("Reel")
        verbose_name_plural = _("Reels")
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(diameter__gt=models.F("diameter_neck")),
                name="reel_diameter_gt_neck",
            ),
            models.CheckConstraint(
                condition=models.Q(max_load__gt=0),
                name="reel_max_load_pos",
            ),
            models.CheckConstraint(
                condition=models.Q(length_neck__gt=0),
                name="reel_length_neck_pos",
            ),
        ]


class ReelType(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Reel type name"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def get_absolute_url(self):
        return reverse("app:reels_list")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _("Reel type")
        verbose_name_plural = _("Reel types")
        ordering = ["name"]


class TransportList(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Transport name"))
    length = models.IntegerField(verbose_name=_("Length (mm)"))
    width = models.IntegerField(verbose_name=_("Width (mm)"))
    height = models.IntegerField(verbose_name=_("Height (mm)"))
    max_load = models.IntegerField(verbose_name=_("Max load (kg)"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def get_absolute_url(self):
        return reverse("app:transport_list_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _("Transport")
        verbose_name_plural = _("Transports")
        ordering = ["created_at"]


class CableLineItem(models.Model):
    cable_cal = models.ForeignKey(
        CableCal,
        related_name="line_items",
        on_delete=models.CASCADE,
        verbose_name=_("Calculation"),
    )
    position = models.PositiveIntegerField(default=0, verbose_name=_("Position"))
    cod = models.CharField(max_length=100, blank=True, verbose_name=_("Cable code"))
    name = models.CharField(max_length=200, blank=True, verbose_name=_("Cable name"))
    con_num = models.PositiveIntegerField(default=1, verbose_name=_("Conductor count"))
    order_len = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Order length (m)"),
    )
    max_len = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Max production length (m)"),
    )
    mass = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        default=Decimal("0"),
        verbose_name=_("Cable mass (kg/m)"),
    )
    diameter = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Cable outer diameter (mm)"),
    )
    # Calculation results
    reel = models.ForeignKey(
        ReelsList,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("Chosen reel"),
    )
    reel_len = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Length per reel (m)"),
    )
    reel_num = models.PositiveIntegerField(default=0, verbose_name=_("Reel count"))
    netto_1 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Netto 1 reel (kg)"),
    )
    brutto_1 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Brutto 1 reel (kg)"),
    )
    netto_all = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Netto total (kg)"),
    )
    brutto_all = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Brutto total (kg)"),
    )
    bending_radius = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Bending radius (mm)"),
    )
    warning = models.TextField(blank=True, default="", verbose_name=_("Warning"))

    class Meta:
        verbose_name = _("Cable line item")
        verbose_name_plural = _("Cable line items")
        ordering = ["position"]

    def __str__(self):
        return f"{self.name} ({self.cod})"