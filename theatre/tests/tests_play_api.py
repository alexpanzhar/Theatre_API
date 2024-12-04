import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.serializers import PlayDetailSerializer, PlayListSerializer

PLAY_URL = reverse("theatre:play-list")


def image_upload_url(play_id):
    return reverse("theatre:play-upload-image", args=[play_id])


def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


def sample_genre(**params):
    defaults = {"name": "Comedy"}
    defaults.update(params)
    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "Emma", "last_name": "Stone"}
    defaults.update(params)
    return Actor.objects.create(**defaults)


def sample_play(**params):
    defaults = {
        "title": "Sample Play",
        "description": "A sample play description",
    }
    defaults.update(params)
    return Play.objects.create(**defaults)


class PlayImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@theatre.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.play = sample_play()

    def tearDown(self):
        self.play.image.delete()

    def test_upload_image_to_play(self):

        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.play.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.play.image.path))

    def test_upload_invalid_image(self):

        url = image_upload_url(self.play.id)
        res = self.client.post(
            url, {"image": "not an image"}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PlayTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@theatre.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        sample_play(title="Play One")
        sample_play(title="Play Two")

        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_filter_plays_by_title(self):
        play = sample_play(title="Romeo and Juliet")
        sample_play(title="Hamlet")

        res = self.client.get(PLAY_URL, {"title": "Romeo"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"][0]["title"], play.title)

    def test_retrieve_play_detail(self):
        play = sample_play()
        play.genres.add(sample_genre())
        play.actors.add(sample_actor())

        url = detail_url(play.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], play.title)


class UnauthenticatedPlayTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_play_list(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_play_detail(self):
        play = sample_play()
        url = detail_url(play.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_play_list(self):
        sample_play()
        play_with_genre = sample_play(title="Action Play")
        genre = sample_genre()
        play_with_genre.genres.add(genre)

        res = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_plays_by_title(self):
        play1 = sample_play(title="Action Play 1")
        play2 = sample_play(title="Drama Play 2")

        res = self.client.get(PLAY_URL, {"title": "Action Play"})
        serializer = PlayListSerializer([play1], many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_plays_by_genre(self):
        genre = sample_genre(name="Action")
        play_with_genre = sample_play(title="Action Play")
        play_with_genre.genres.add(genre)
        sample_play(title="Drama Play")

        res = self.client.get(PLAY_URL, {"genres": genre.id})
        serializer = PlayListSerializer([play_with_genre], many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_play_detail(self):
        play = sample_play()
        play.genres.add(sample_genre(name="Action"))
        play.actors.add(sample_actor(first_name="Tom", last_name="Cruise"))

        url = detail_url(play.id)
        res = self.client.get(url)
        serializer = PlayDetailSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AuthenticatedStaffPlayTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.test", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        genre = sample_genre()
        actor = sample_actor()
        payload = {
            "title": "New Play",
            "description": "A new action play.",
            "genres": [genre.id],
            "actors": [actor.id],
        }
        res = self.client.post(PLAY_URL, payload)
        play = Play.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(play.title, payload["title"])
        self.assertEqual(play.description, payload["description"])
        self.assertEqual(list(play.genres.all()), [genre])
        self.assertEqual(list(play.actors.all()), [actor])

    def test_update_play(self):
        play = sample_play()
        payload = {"title": "Updated Play Title"}
        url = detail_url(play.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        play.refresh_from_db()
        self.assertEqual(play.title, payload["title"])

    def test_delete_play(self):
        play = sample_play()
        url = detail_url(play.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        plays = Play.objects.filter(id=play.id)
        self.assertEqual(plays.count(), 0)
