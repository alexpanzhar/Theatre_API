import logging
from datetime import datetime

from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from theatre.models import Genre, Actor, TheatreHall, Play, Performance, Reservation
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PerformanceSerializer,
    PerformanceListSerializer, PerformanceDetailSerializer, ReservationListSerializer, ReservationSerializer,
)

# Create your views here.

logger = logging.getLogger(__name__)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("genres", "actors")

    def _filter_by_ids(self, queryset, param_name, field_name):
        """Filter queryset by a comma-separated list of IDs."""
        ids = self.request.query_params.get(param_name)
        if not ids:
            return queryset
        try:
            id_list = map(int, ids.split(","))
            return queryset.filter(**{f"{field_name}__id__in": id_list})
        except ValueError:
            logger.warning(f"Invalid ID list for {param_name}: {ids}")
            return queryset.none()

    def get_queryset(self):
        """Retrieve plays with optional filters."""
        queryset = self.queryset
        title = self.request.query_params.get("title")

        if title:
            queryset = queryset.filter(title__icontains=title)

        queryset = self._filter_by_ids(queryset, "genres", "genres")
        queryset = self._filter_by_ids(queryset, "actors", "actors")

        return queryset.distinct()

    def get_serializer_class(self):

        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer

        return PlaySerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all().select_related("play", "theatre_hall")

    def get_queryset(self):
        date = self.request.query_params.get("date")
        play_id_str = self.request.query_params.get("play")

        queryset = self.queryset

        try:
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                queryset = queryset.filter(show_time__date=date)
            if play_id_str:
                queryset = queryset.filter(play_id=int(play_id_str))
        except (ValueError, TypeError):
            return self.queryset.none()
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__theatre_hall",
        "tickets__performance__play"
    )
    pagination_class = ReservationPagination
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
