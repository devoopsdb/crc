from django.contrib import admin

from .models import CableCal, ReelsList, ReelType, TransportList


class CableCalAdmin(admin.ModelAdmin):
    list_display = ("id", "order_num", "cod", "name", "created_at", "updated_at")
    list_display_links = ("id", "order_num")
    search_fields = ("order_num", "cod", "name")


class ReelsListAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "diameter", "reel_type", "created_at", "updated_at")
    list_display_links = ("id", "name")
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
admin.site.register(ReelsList, ReelsListAdmin)
admin.site.register(TransportList, TransportListAdmin)
admin.site.register(ReelType, ReelTypeAdmin)
