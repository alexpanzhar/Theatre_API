from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import localtime
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from theatre.models import Performance, Play, TheatreHall
from theatre.serializers import (
    PerformanceListSerializer,
    PerformanceDetailSerializer,
)

PERFORMANCE_URL = reverse("theatre:performance-list")


def detail_url(performance_id):

    return reverse("theatre:performance-detail", args=[performance_id])


def sample_play(**params):

    defaults = {"title": "Sample Play", "description": "Sample Description"}
    defaults.update(params)
    return Play.objects.create(**defaults)


def sample_theatre_hall(**params):

    defaults = {"name": "Main Hall", "rows": 10, "seats_in_row": 10}
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def sample_performance(**params):

    defaults = {
        "play": sample_play(),
        "theatre_hall": sample_theatre_hall(),
        "show_time": "2024-12-15T19:00:00Z",
    }
    defaults.update(params)
    return Performance.objects.create(**defaults)


class UnauthenticatedPerformanceTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_list(self):

        res = self.client.get(PERFORMANCE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_detail(self):

        performance = sample_performance()
        url = detail_url(performance.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPerformanceTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_list_performances(self):

        sample_performance()

        res = self.client.get(PERFORMANCE_URL)
        performances = Performance.objects.all()
        serializer = PerformanceListSerializer(performances, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_performance_detail(self):

        performance = sample_performance()
        url = detail_url(performance.id)
        res = self.client.get(url)
        serializer = PerformanceDetailSerializer(performance)

        expected_data = serializer.data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)

    def test_create_performance_forbidden(self):

        play = sample_play()
        theatre_hall = sample_theatre_hall()
        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": "2024-12-20T18:00:00+00:00",
        }
        res = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedStaffPerformanceTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_performance(self):

        play = sample_play()
        theatre_hall = sample_theatre_hall()
        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": "2024-12-20T18:00:00+00:00",
        }
        res = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        performance = Performance.objects.get(id=res.data["id"])
        self.assertEqual(performance.play, play)
        self.assertEqual(performance.theatre_hall, theatre_hall)
        self.assertEqual(
            performance.show_time.isoformat(), payload["show_time"]
        )

    def test_update_performance(self):

        performance = sample_performance()
        play = sample_play(title="New Play")
        payload = {"play": play.id}
        url = detail_url(performance.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        performance.refresh_from_db()
        self.assertEqual(performance.play, play)

    def test_delete_performance(self):

        performance = sample_performance()
        url = detail_url(performance.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Performance.objects.filter(id=performance.id).exists()
        )
