from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from theatre.models import Reservation, Ticket, Performance, TheatreHall, Play

RESERVATION_URL = reverse("theatre:reservation-list")


def sample_theatre_hall(**params):
    defaults = {"name": "Main Hall", "rows": 10, "seats_in_row": 10}
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def sample_play(**params):
    defaults = {"title": "Sample Play", "description": "Sample description"}
    defaults.update(params)
    return Play.objects.create(**defaults)


def sample_performance(**params):
    defaults = {
        "play": sample_play(),
        "theatre_hall": sample_theatre_hall(),
        "show_time": "2024-12-01T19:00:00+00:00",
    }
    defaults.update(params)
    return Performance.objects.create(**defaults)


def sample_reservation(user, **params) -> Reservation:
    defaults = {"user": user}
    defaults.update(params)
    return Reservation.objects.create(**defaults)


class UnauthenticatedReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="password"
        )

    def test_auth_required_for_reservation_list(self):
        reservation = sample_reservation(user=self.user)
        Ticket.objects.create(
            reservation=reservation,
            performance=sample_performance(),
            row=1,
            seat=1,
        )

        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_creating_reservation(self):
        payload = {
            "performance": sample_performance().id,  # Adjust this field as per your Reservation model
        }
        res = self.client.post(RESERVATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@theatre.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_list_reservations(self):
        performance = sample_performance()
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            reservation=reservation, performance=performance, row=1, seat=1
        )

        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_create_reservation(self):
        performance = sample_performance()
        payload = {
            "tickets": [{"row": 1, "seat": 1, "performance": performance.id}],
        }

        res = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        reservation = Reservation.objects.get(id=res.data["id"])
        self.assertEqual(reservation.tickets.count(), 1)
