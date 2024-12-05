import pytz
from django.test import TestCase
from theatre.models import Actor, Genre, Play, TheatreHall, Performance, Ticket
from datetime import datetime
from django.utils.timezone import make_aware


class ActorModelTest(TestCase):
    def setUp(self):
        self.actor = Actor.objects.create(first_name="John", last_name="Doe")

    def test_actor_full_name(self):
        self.assertEqual(self.actor.full_name, "John Doe")

    def test_actor_str(self):
        self.assertEqual(str(self.actor), "John Doe")


class GenreModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Drama")

    def test_genre_str(self):
        self.assertEqual(str(self.genre), "Drama")


class PlayModelTest(TestCase):
    def setUp(self):
        self.actor1 = Actor.objects.create(first_name="John", last_name="Doe")
        self.actor2 = Actor.objects.create(
            first_name="Jane", last_name="Smith"
        )
        self.genre = Genre.objects.create(name="Comedy")
        self.play = Play.objects.create(
            title="Funny Play", description="A great comedy."
        )
        self.play.actors.set([self.actor1, self.actor2])
        self.play.genres.add(self.genre)

    def test_play_str(self):
        self.assertEqual(str(self.play), "Funny Play")

    def test_play_actors(self):
        self.assertEqual(
            list(self.play.actors.all()), [self.actor1, self.actor2]
        )

    def test_play_genres(self):
        self.assertIn(self.genre, self.play.genres.all())


class TheatreHallModelTest(TestCase):
    def setUp(self):
        self.hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=15
        )

    def test_theatre_hall_capacity(self):
        self.assertEqual(self.hall.capacity, 150)

    def test_theatre_hall_str(self):
        self.assertEqual(str(self.hall), "Main Hall")


class PerformanceModelTest(TestCase):
    def setUp(self):
        self.play = Play.objects.create(
            title="Funny Play", description="A great comedy."
        )
        self.hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=15
        )
        self.performance = Performance.objects.create(
            show_time=make_aware(
                datetime(2024, 12, 1, 19, 30), timezone=pytz.UTC
            ),
            play=self.play,
            theatre_hall=self.hall,
        )

    def test_performance_str(self):
        self.assertEqual(
            str(self.performance), "Funny Play 2024-12-01 19:30:00+00:00"
        )


class TicketModelTest(TestCase):
    def setUp(self):
        self.hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=15
        )
        self.play = Play.objects.create(
            title="Funny Play", description="A great comedy."
        )
        self.performance = Performance.objects.create(
            show_time=make_aware(datetime(2024, 12, 1, 19, 30)),
            play=self.play,
            theatre_hall=self.hall,
        )

    def test_ticket_validation(self):
        # Valid ticket
        Ticket.validate_ticket(5, 10, self.hall, ValueError)

        # Invalid row
        with self.assertRaises(ValueError):
            Ticket.validate_ticket(11, 10, self.hall, ValueError)

        # Invalid seat
        with self.assertRaises(ValueError):
            Ticket.validate_ticket(5, 16, self.hall, ValueError)
