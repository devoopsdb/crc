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
        max_length=50, unique=True, db_index=True, verbose_name="Sifarişin nömrəsi"
    )
    cod = models.TextField(verbose_name="Kabelin kodu")
    name = models.TextField(db_index=True, verbose_name="Kabelin adı")
    mass = models.TextField(verbose_name="Kabelin çəkisi, kq/m")
    diameter = models.TextField(verbose_name="Kabelin xarici diametri, mm")
    con_num = models.TextField(verbose_name="Kabelin cəriyan keçirən damarların sayı")
    order_len = models.TextField(verbose_name="sifarişin uzunluğu, m")
    max_len = models.TextField(verbose_name="maksimal istehsalat uzunluğu, m")
    transport = models.ForeignKey(
        "TransportList", null=True, blank=False, on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaradılma tarixi"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yeniləmə tarixi")
    reel_name = models.TextField(verbose_name="Baraban adı", blank=True)
    reel_type = models.TextField(verbose_name="Baraban növü", blank=True)
    reel_num = models.TextField(verbose_name="Baraban sayı", blank=True)
    reel_len = models.TextField(
        verbose_name="Bir barabana dolanan miqdar, m", blank=True
    )
    bending_radius = models.TextField(verbose_name="Əyilmə radiusu", blank=True)
    netto_1 = models.TextField(verbose_name="Netto 1 baraban", blank=True)
    brutto_1 = models.TextField(verbose_name="Brutto 1 baraban", blank=True)
    netto_all = models.TextField(verbose_name="Netto ümumi", blank=True)
    brutto_all = models.TextField(verbose_name="Brutto ümumi", blank=True)
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
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]


class ReelsList(models.Model):
    name = models.CharField(max_length=50, verbose_name="Barabanın adı")
    height = models.IntegerField(verbose_name="Barabanın hündürlükü abşıvkalı, mm")
    width = models.IntegerField(verbose_name="Barabanın eni, mm")
    diameter = models.IntegerField(verbose_name="Barabanın diametri, mm")
    diameter_neck = models.IntegerField(
        verbose_name="Barabanın boğazının diametiri, mm"
    )
    length_neck = models.IntegerField(verbose_name="Barabanın bogazının uzunluğu, mm")
    max_load = models.IntegerField(verbose_name="Maksimal yükləmə, kq")
    mass = models.IntegerField(verbose_name="Barabanın çəkisi, kq")
    reel_type = models.ForeignKey(
        "ReelType",
        verbose_name="Barabanın növü",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaradılma tarixi"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yeniləmə tarixi")

    def get_absolute_url(self):
        return reverse("app:reels_list_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Reel"
        verbose_name_plural = "Reels"
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
    name = models.CharField(max_length=50, verbose_name="Barabanın növü")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaradılma tarixi"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yeniləmə tarixi")

    def get_absolute_url(self):
        return reverse("app:reels_list")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Reel Type"
        verbose_name_plural = "Reel Types"
        ordering = ["name"]


class TransportList(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nəqliyətin adı")
    length = models.IntegerField(verbose_name="Uzunluq, mm")
    width = models.IntegerField(verbose_name="En, mm")
    height = models.IntegerField(verbose_name="Hündürlük, mm")
    max_load = models.IntegerField(verbose_name="maksimal yükləmə, kq")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaradılma tarixi"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yeniləmə tarixi")

    def get_absolute_url(self):
        return reverse("app:transport_list_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Transport"
        verbose_name_plural = "Transports"
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