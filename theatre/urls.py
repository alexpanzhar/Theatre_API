from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    GenreViewSet,
    ActorViewSet,
    TheatreHallViewSet,
    PlayViewSet,
    PerformanceViewSet,
    ReservationViewSet,
)

app_name = "theatre"

router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("theatre-halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("plays", PlayViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
