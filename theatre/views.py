from rest_framework import viewsets

from theatre.models import Genre, Actor, TheatreHall
from theatre.serializers import GenreSerializer, ActorSerializer, TheatreHallSerializer


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
