from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from app_run.models import Run


class TestOptimizationUserEndPoint(APITestCase):

    def setUp(self):
        for i in range(25):

            user = get_user_model().objects.create_user(
                username=f'testuser{i}',
                password='password123',
                email='test@example.com'
            )

            for j in range(5):
                Run.objects.create(
                    athlete=user,
                    comment=f'Comment {j}',
                    status=Run.Status.FINISHED,
                )

    def test_runs_finished_optimization_user_detail(self):

        with self.assertNumQueries(3):
            response = self.client.get(reverse('users-detail', args=[1]))

        self.assertEqual(response.status_code, 200)

    def test_runs_finished_optimization_users_list(self):
        with self.assertNumQueries(2):
            response = self.client.get(reverse('users-list'))

        self.assertEqual(response.status_code, 200)
