from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from theatre.models import Genre

GENRE_URL = reverse("theatre:genre-list")


def detail_url(genre_id):
    return reverse("theatre:genre-detail", args=[genre_id])


def sample_genre(**params):
    defaults = {"name": "Sample Genre"}
    defaults.update(params)
    return Genre.objects.create(**defaults)


class UnauthenticatedGenreTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_list(self):
        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_detail(self):
        genre = sample_genre()
        url = detail_url(genre.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserGenreTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_list_genres(self):
        sample_genre(name="Action")
        sample_genre(name="Drama")

        res = self.client.get(GENRE_URL)
        genres = Genre.objects.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), genres.count())

    def test_retrieve_genre_detail(self):
        genre = sample_genre(name="Action")
        url = detail_url(genre.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], genre.id)
        self.assertEqual(res.data["name"], genre.name)

    def test_create_genre_forbidden(self):
        payload = {"name": "Comedy"}
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedStaffGenreTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_genres(self):
        sample_genre(name="Action")
        sample_genre(name="Drama")

        res = self.client.get(GENRE_URL)
        genres = Genre.objects.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), genres.count())

    def test_create_genre(self):

        payload = {"name": "Comedy"}
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        genre = Genre.objects.get(id=res.data["id"])
        self.assertEqual(genre.name, payload["name"])

    def test_create_genre_invalid(self):

        payload = {"name": ""}
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_genre_detail(self):

        genre = sample_genre(name="Action")
        url = detail_url(genre.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], genre.id)
        self.assertEqual(res.data["name"], genre.name)

    def test_update_genre(self):

        genre = sample_genre(name="Action")
        payload = {"name": "Adventure"}
        url = detail_url(genre.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        genre.refresh_from_db()
        self.assertEqual(genre.name, payload["name"])

    def test_delete_genre(self):

        genre = sample_genre(name="Action")
        url = detail_url(genre.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Genre.objects.filter(id=genre.id).exists())
