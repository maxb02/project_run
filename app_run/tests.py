from django.test import TestCase

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from .models import Run, Challenge, Positions
from .utils import calculate_distance


class ChallengeRun10Test(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )

        for i in range(25):
            Run.objects.create(
                athlete=self.user,
                comment=f'Comment {i}',
                status=Run.Status.IN_PROGRESS,
            )

    def test_run10_challenge(self):
        self.assertEqual(Challenge.objects.count(), 0)

        for i in range(1, 11):
            response = self.client.post(reverse('run-stop', args=[i]), data={})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Challenge.objects.filter(athlete=self.user).count(), 1)
        self.assertEqual(Run.objects.filter(status=Run.Status.FINISHED).count(), 10)

        for i in range(11, 26):
            response = self.client.post(reverse('run-stop', args=[i]), data={})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Challenge.objects.filter(athlete=self.user).count(), 1)
        self.assertEqual(Challenge.objects.count(), 1)


class ChallengeEndpointTest(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username="testuser1", password="pass123")
        self.user2 = get_user_model().objects.create_user(username="testuser2", password="pass123")

        self.challenge1 = Challenge.objects.create(
            athlete=self.user1,
        )
        self.challenge2 = Challenge.objects.create(
            athlete=self.user2,
        )

    def test_challenge_list(self):
        response = self.client.get(reverse('challenges'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_challenge_athlete_filter(self):
        response = self.client.get(reverse('challenges'), data={'athlete': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(reverse('challenges'), data={'athlete': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class PositionsEndpointTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )

        self.run_init = Run.objects.create(athlete=self.user,
                                           comment='Test Run',
                                           status=Run.Status.INIT)
        self.run_in_progress = Run.objects.create(athlete=self.user,
                                                  comment='Test Run',
                                                  status=Run.Status.IN_PROGRESS)
        self.run_finished = Run.objects.create(athlete=self.user,
                                               comment='Test Run',
                                               status=Run.Status.FINISHED)

        self.run_in_progress1 = Run.objects.create(athlete=self.user,
                                                   comment='Test Run 1',
                                                   status=Run.Status.IN_PROGRESS)
        self.position1 = Positions.objects.create(
            run=self.run_in_progress1,
            longitude=33,
            latitude=44
        )

        self.run_in_progress2 = Run.objects.create(athlete=self.user,
                                                   comment='Test Run 2',
                                                   status=Run.Status.IN_PROGRESS)
        self.position2 = Positions.objects.create(
            run=self.run_in_progress2,
            longitude=55,
            latitude=66
        )

    def test_position_list(self):
        response = self.client.get(reverse('positions-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_detail_position_for_run(self):
        response = self.client.get(reverse('positions-list'), data={'run': self.run_in_progress1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.position1.id)
        self.assertEqual(response.data[0]['longitude'], self.position1.longitude)
        self.assertEqual(response.data[0]['latitude'], self.position1.latitude)
        self.assertEqual(response.data[0]['run'], self.run_in_progress1.id)

    def test_position_delete(self):
        response = self.client.delete(reverse('positions-detail', args=[self.position1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Positions.objects.filter(id=self.position1.id).exists(), False)

    def test_position_longitude_validation(self):
        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -181,
                                                                     'latitude': 22})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': 181,
                                                                     'latitude': 22})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -180,
                                                                     'latitude': 22})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': 180,
                                                                     'latitude': 22})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_position_latitude_validation(self):
        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -33,
                                                                     'latitude': -91})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': 33,
                                                                     'latitude': 91})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -180,
                                                                     'latitude': 90})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -180,
                                                                     'latitude': -90})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_position_run_validation(self):
        response = self.client.post(reverse('positions-list'), data={'run': self.run_init.id,
                                                                     'longitude': -33,
                                                                     'latitude': -33})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_finished.id,
                                                                     'longitude': -33,
                                                                     'latitude': -33})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -33,
                                                                     'latitude': -33})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CalculateDistanceRun(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        self.run = Run.objects.create(athlete=self.user,
                                      comment='Test Run',
                                      status=Run.Status.IN_PROGRESS)
        Positions.objects.create(run=self.run,
                                 latitude=41.49008,
                                 longitude=-71.312796)
        Positions.objects.create(run=self.run,
                                 latitude=41.499498,
                                 longitude=-81.695391)
        self.distance = 866.4554329098687

    def test_calculate_distance(self):
        distance = calculate_distance(self.run.id)
        self.assertEqual(distance, 866.4554329098687)
        run = Run.objects.get(id=self.run.id)
        self.assertEqual(run.distance, 866.4554329098687)

    def test_calculate_distance_run_stop_endpoint(self):
        response = self.client.post(reverse('run-stop', args=[self.run.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('runs-detail', args=[self.run.id]))
        self.assertEqual(response.data['distance'], 866.4554329098687)
