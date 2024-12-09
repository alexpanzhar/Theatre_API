from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from theatre.models import TheatreHall
from theatre.serializers import TheatreHallSerializer

THEATRE_HALL_URL = reverse("theatre:theatrehall-list")


def detail_url(theatre_hall_id: int):
    return reverse("theatre:theatrehall-detail", args=[theatre_hall_id])


def sample_theatre_hall(**params) -> TheatreHall:
    defaults = {"name": "Main Hall", "rows": 10, "seats_in_row": 10}
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


class UnauthenticatedTheatreHallTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_theatre_hall_list(self):
        res = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_theatre_hall_detail(self):
        theatre_hall = sample_theatre_hall()
        url = detail_url(theatre_hall.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTheatreHallTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_list_theatre_halls(self):
        sample_theatre_hall(name="Main Hall", rows=10, seats_in_row=10)
        sample_theatre_hall(name="Small Hall", rows=10, seats_in_row=10)

        res = self.client.get(THEATRE_HALL_URL)
        theatre_halls = TheatreHall.objects.all().order_by("id")
        serializer = TheatreHallSerializer(theatre_halls, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_theatre_hall_detail(self):
        theatre_hall = sample_theatre_hall()
        url = detail_url(theatre_hall.id)
        res = self.client.get(url)
        serializer = TheatreHallSerializer(theatre_hall)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AuthenticatedStaffTheatreHallTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_theatre_hall(self):
        payload = {"name": "New Hall", "rows": 10, "seats_in_row": 10}
        res = self.client.post(THEATRE_HALL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        theatre_hall = TheatreHall.objects.get(id=res.data["id"])
        self.assertEqual(theatre_hall.name, payload["name"])
        self.assertEqual(theatre_hall.capacity, 100)

    def test_update_theatre_hall(self):
        theatre_hall = sample_theatre_hall(
            name="Old Hall", rows=10, seats_in_row=10
        )
        payload = {"name": "Updated Hall", "rows": 5, "seats_in_row": 5}
        url = detail_url(theatre_hall.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        theatre_hall.refresh_from_db()
        self.assertEqual(theatre_hall.name, payload["name"])
        self.assertEqual(theatre_hall.capacity, 25)

    def test_delete_theatre_hall(self):
        theatre_hall = sample_theatre_hall()
        url = detail_url(theatre_hall.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            TheatreHall.objects.filter(id=theatre_hall.id).exists()
        )
