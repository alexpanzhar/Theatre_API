import logging
from datetime import datetime

from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from theatre.models import (
    Genre,
    Actor,
    TheatreHall,
    Play,
    Performance,
    Reservation,
)
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationListSerializer,
    ReservationSerializer,
    PlayImageSerializer,
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
        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(item, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type={
                    "type": "string",
                },
                description="Filter by title (ex. ?title='some_title')",
            ),
            OpenApiParameter(
                "genres",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by genres id's (ex. ?genres=1,2,n)",
            ),
            OpenApiParameter(
                "actors",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by actors id's (ex. ?actors=1,2,n)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of movies"""
        return super().list(request, *args, **kwargs)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = (
        Performance.objects.all()
        .select_related("play", "theatre_hall")
        .annotate(
            tickets_available=(
                    F("theatre_hall__rows")
                    * F("theatre_hall__seats_in_row")
                    - Count("tickets")
            )
        )
    )

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                type={
                    "type": "date",
                },
                description="Filter by date (ex. ?date='year-month-day')",
            ),
            OpenApiParameter(
                "play",
                type={
                    "type": "number",
                },
                description="Filter by plays id's (ex. ?play=1)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of MovieSessions"""
        return super().list(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__theatre_hall", "tickets__performance__play"
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
