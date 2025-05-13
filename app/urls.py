from django.urls import path

from .views import *

urlpatterns = [
    path("", CableCalView.as_view(), name="cable_cal"),
    path("reels_list/", ReelsListView.as_view(), name="reels_list"),
    path("cable_list/<int:pk>", CableCalDetail.as_view(), name="cable_detail"),
    path("cable_list/<int:pk>/del/", CableCalDel.as_view(), name="cable_del"),
    path("reels_list/<int:pk>", ReelsListDetail.as_view(), name="reels_list_detail"),
    path("reels_list/add/", ReelsListCreate.as_view(), name="reels_add"),
    path("reels_list/<int:pk>/del", ReelsListDel.as_view(), name="reels_del"),
    path("transport_list/", TransportListView.as_view(), name="transport_list"),
    path(
        "transport_list_/<int:pk>",
        TransportListDetail.as_view(),
        name="transport_list_detail",
    ),
    path("transport_list/add/", TransportListCreate.as_view(), name="transport_add"),
    path(
        "transport_list/<int:pk>/del/", TransportListDel.as_view(), name="transport_del"
    ),
    path("cable_list/", CableCalList.as_view(), name="cable_list"),
    path("x/", x),
]
