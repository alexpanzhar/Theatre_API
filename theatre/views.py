from rest_framework import viewsets

from theatre.models import Genre
from theatre.serializers import GenreSerializer


# Create your views here.

class GenreViewSet(viewsets.ModelViewSet
                   ):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
