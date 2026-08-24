from django.contrib import admin

from .models import (
    CableCal,
    CableLineItem,
    CalculationSettings,
    ReelType,
    ReelsList,
    TransportList,
)


class CableLineItemInline(admin.TabularInline):
    """Per-line results are read-only (computed by the calculation view)."""

    model = CableLineItem
    extra = 0
    fields = (
        "position", "cod", "name", "con_num", "order_len", "max_len",
        "mass", "diameter", "reel", "reel_len", "reel_num",
        "netto_1", "brutto_1", "netto_all", "brutto_all",
        "bending_radius", "warning",
    )
    readonly_fields = (
        "reel", "reel_len", "reel_num", "netto_1", "brutto_1",
        "netto_all", "brutto_all", "bending_radius", "warning",
    )


class CableCalAdmin(admin.ModelAdmin):
    list_display = ("id", "order_num", "transport", "created_at")
    list_display_links = ("id", "order_num")
    list_select_related = ("transport",)
    search_fields = ("order_num",)
    inlines = [CableLineItemInline]


class CalculationSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "winding_margin_mm", "packing_factor", "bending_radius_multiplier")
    # Singleton: at most one row; never delete it.
    def has_add_permission(self, request):
        return not CalculationSettings.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False


class ReelsListAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "diameter", "reel_type", "created_at", "updated_at")
    list_display_links = ("id", "name")
    list_select_related = ("reel_type",)
    search_fields = ("name", "diameter")


class TransportListAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name",)


class ReelTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name",)


admin.site.register(CableCal, CableCalAdmin)
admin.site.register(CalculationSettings, CalculationSettingsAdmin)
admin.site.register(ReelsList, ReelsListAdmin)
admin.site.register(TransportList, TransportListAdmin)
admin.site.register(ReelType, ReelTypeAdmin)