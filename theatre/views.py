from rest_framework import viewsets

from theatre.models import Genre, Actor, TheatreHall, Play
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
)


# Create your views here.


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
    serializer_class = PlaySerializer

    def _filter_by_ids(self, queryset, param_name, field_name):
        """Filter queryset by a comma-separated list of IDs."""
        ids = self.request.query_params.get(param_name)
        if ids:
            try:
                id_list = [int(str_id) for str_id in ids.split(",")]
                return queryset.filter(**{f"{field_name}__id__in": id_list})
            except ValueError:
                return queryset
        return queryset

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
