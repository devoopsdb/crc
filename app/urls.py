from django.urls import path

from .views import (
    CableCalDel,
    CableCalDetail,
    CableCalList,
    CableCalView,
    ReelsListCreate,
    ReelsListDel,
    ReelsListDetail,
    ReelsListView,
    TransportListCreate,
    TransportListDel,
    TransportListDetail,
    TransportListView,
)

app_name = "app"

urlpatterns = [
    path("", CableCalView.as_view(), name="cable_cal"),
    path("cables/", CableCalList.as_view(), name="cable_list"),
    path("cables/<int:pk>/", CableCalDetail.as_view(), name="cable_detail"),
    path("cables/<int:pk>/delete/", CableCalDel.as_view(), name="cable_del"),
    path("reels/", ReelsListView.as_view(), name="reels_list"),
    path("reels/<int:pk>/", ReelsListDetail.as_view(), name="reels_list_detail"),
    path("reels/add/", ReelsListCreate.as_view(), name="reels_add"),
    path("reels/<int:pk>/delete/", ReelsListDel.as_view(), name="reels_del"),
    path("transport/", TransportListView.as_view(), name="transport_list"),
    path("transport/<int:pk>/", TransportListDetail.as_view(), name="transport_list_detail"),
    path("transport/add/", TransportListCreate.as_view(), name="transport_add"),
    path("transport/<int:pk>/delete/", TransportListDel.as_view(), name="transport_del"),
]