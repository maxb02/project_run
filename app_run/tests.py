from django.test import TestCase

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from .models import Run, Challenge



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

    def test_multiple_starts_and_check_status(self):
        self.assertEqual(Challenge.objects.count(), 0)

        for i in range(1,11):
            response = self.client.post(reverse('run-stop', args=[i]), data= {})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Challenge.objects.filter(athlete=self.user).count(), 1)
        self.assertEqual(Run.objects.filter(status=Run.Status.FINISHED).count(), 10)


        for i in range(11,26):
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
