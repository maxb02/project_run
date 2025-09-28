import os
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.models import CollectibleItem
from app_run.models import Run, Challenge, Positions
from app_run.utils import calculate_run_distance, award_challenge_if_completed_run_50km, calculate_run_time_in_seconds
from app_run.utils import collect_item_if_nearby


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
                                                                     'latitude': 22,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': 181,
                                                                     'latitude': 22,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -180,
                                                                     'latitude': 22,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': 180,
                                                                     'latitude': 22,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_position_latitude_validation(self):
        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -33,
                                                                     'latitude': -91,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': 33,
                                                                     'latitude': 91,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -58.3702,
                                                                     'latitude': -234434.6083,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -180,
                                                                     'latitude': 90,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -180,
                                                                     'latitude': -90,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_position_run_validation(self):
        response = self.client.post(reverse('positions-list'), data={'run': self.run_init.id,
                                                                     'longitude': -33,
                                                                     'latitude': -33,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_finished.id,
                                                                     'longitude': -33,
                                                                     'latitude': -33,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'longitude': -33,
                                                                     'latitude': -33,
                                                                     'date_time': '2024-10-12T14:42:15.123456', })
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
        distance = calculate_run_distance(self.run.id)
        self.assertEqual(distance, 866.4554329098687)
        run = Run.objects.get(id=self.run.id)
        self.assertEqual(run.distance, 866.4554329098687)

    def test_calculate_distance_run_stop_endpoint(self):
        response = self.client.post(reverse('run-stop', args=[self.run.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('runs-detail', args=[self.run.id]))
        self.assertEqual(response.data['distance'], 866.4554329098687)


class Run50kmChalengeTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        Run.objects.create(athlete=self.user,
                           comment='Test Run',
                           status=Run.Status.FINISHED,
                           distance=45)
        Run.objects.create(athlete=self.user,
                           comment='Test Run',
                           status=Run.Status.FINISHED,
                           distance=10)

    def test_award_challenge_if_completed_run_50km(self):
        self.assertEqual(self.user.challenges.filter(full_name=Challenge.NameChoices.RUN50KM).count(), 0)
        award_challenge_if_completed_run_50km(athlete_id=self.user.id)
        self.assertEqual(self.user.challenges.filter(full_name=Challenge.NameChoices.RUN50KM).count(), 1)
        Run.objects.create(athlete=self.user,
                           comment='Test Run',
                           status=Run.Status.FINISHED,
                           distance=55)
        award_challenge_if_completed_run_50km(athlete_id=self.user.id)
        self.assertEqual(self.user.challenges.filter(full_name=Challenge.NameChoices.RUN50KM).count(), 1)


class CollectibleItemsFileUplodadTest(APITestCase):
    def test_file_upload(self):
        self.assertEqual(CollectibleItem.objects.count(), 0)

        file_name = 'upload_example.xlsx'
        path = os.path.join(settings.BASE_DIR, 'app_run', 'tests', 'fixtures', file_name, )
        with open(path, 'rb') as f:
            file = SimpleUploadedFile(file_name, f.read(),
                                      content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                      )

        response = self.client.post(
            reverse('upload-file'),
            {"file": file},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(CollectibleItem.objects.count(), 2)


class CollectibleItemsEndpointTest(APITestCase):
    def setUp(self):
        CollectibleItem.objects.create(name='Test1',
                                       uid='asd',
                                       latitude=11,
                                       longitude=22,
                                       picture='https:\\test.com',
                                       value=1)
        CollectibleItem.objects.create(name='Test2',
                                       uid='asd',
                                       latitude=11,
                                       longitude=22,
                                       picture='https:\\test.com',
                                       value=3)

    def test_endpoint_list(self):
        response = self.client.get(reverse('collectible_item-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class CollectibleItemsTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com',

        )
        self.coleectible_item1 = CollectibleItem.objects.create(name='Test1',
                                                                uid='asd',
                                                                latitude=11,
                                                                longitude=22,
                                                                picture='https:\\test.com',
                                                                value=1,
                                                                user=self.user)
        self.coleectible_item2 = CollectibleItem.objects.create(name='Test2',
                                                                uid='asd',
                                                                latitude=11,
                                                                longitude=22,
                                                                picture='https:\\test.com',
                                                                value=3,
                                                                user=self.user)

    def test_endpoint_list(self):
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0]),
                         {'date_joined', 'runs_finished', 'id', 'last_name', 'first_name', 'username', 'type'})

    def test_endpoint_detail(self):
        response = self.client.get(reverse('users-detail', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data),
                         {'date_joined', 'runs_finished', 'id', 'last_name', 'first_name', 'username', 'type', 'items'})


class CollectItemNearbyUnitTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com',

        )

        self.item1 = CollectibleItem.objects.create(
            name="Item1",
            uid="item1uid",
            latitude=40.0000,
            longitude=29.0000,
            picture="http://example.com/item1.png",
            value=100
        )

        self.item2 = CollectibleItem.objects.create(
            name="Item2",
            uid="item2uid",
            latitude=40.0020,
            longitude=29.0020,
            picture="http://example.com/item2.png",
            value=200
        )

    @patch("app_run.utils.geodesic")
    def test_collect_item_if_nearby(self, mock_geodesic):
        near = MagicMock()
        near.meters = 50
        far = MagicMock()
        far.meters = 200

        mock_geodesic.side_effect = [near, far]

        collected = collect_item_if_nearby(10, 10, self.user)

        self.assertIn(self.item1, collected)
        self.assertNotIn(self.item2, collected)
        self.assertTrue(self.user.collectible_items.filter(id=self.item1.id).exists())


class CollectItemNearbyUnitTestCase(APITestCase):
    ITEM_POSITION = (50.4501, 30.5234)
    DISTANCE_50_METER = (50.45055, 30.5234)
    DISTANCE_150_METER = (50.45145, 30.5234)

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com',

        )

        self.item = CollectibleItem.objects.create(
            name="Item1",
            uid="item1uid",
            latitude=self.ITEM_POSITION[0],
            longitude=self.ITEM_POSITION[1],
            picture="http://example.com/item1.png",
            value=100
        )

        self.run_in_progress = Run.objects.create(athlete=self.user,
                                                  comment='Test Run 1',
                                                  status=Run.Status.IN_PROGRESS)

    def test_endpoint_create_position_far_from_collect_item(self):
        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'latitude': self.DISTANCE_150_METER[0],
                                                                     'longitude': self.DISTANCE_150_METER[1],
                                                                     'date_time': '2024-10-12T14:42:15.123456',
                                                                     })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.collectible_items.count(), 0)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'latitude': self.DISTANCE_50_METER[0],
                                                                     'longitude': self.DISTANCE_50_METER[1],
                                                                     'date_time': '2024-10-12T14:42:15.123456',
                                                                     })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.collectible_items.count(), 1)

        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'latitude': '-234434.6083',
                                                                     'longitude': '-58.3702',
                                                                     }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user.collectible_items.count(), 1)

    def test_endpoint_user_collectible_item(self):
        self.user.collectible_items.add(self.item)
        response = self.client.get(reverse('users-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.json())
        self.assertIsInstance(response.json().get("items"), list)
        self.assertIsInstance(response.json().get("items")[0], dict)


class RunTimeTestCase(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com',

        )
        self.run_in_progress = Run.objects.create(athlete=self.user,
                                                  comment='Test Run 1',
                                                  status=Run.Status.IN_PROGRESS)

    def test_position_endpoint_run_time_field(self):
        response = self.client.post(reverse('positions-list'), data={'run': self.run_in_progress.id,
                                                                     'latitude': 11,
                                                                     'longitude': 22,
                                                                     'date_time': '2024-10-12T14:30:15.123456',
                                                                     })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('positions-detail', args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('date_time'), '2024-10-12T14:30:15.123456')

    def test_calculate_run_time_in_seconds(self):
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11,
            longitude=22,
            date_time='2024-10-12T14:30:15.123456',

        )
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11.1,
            longitude=22.1,
            date_time='2024-10-12T14:31:15.123456',

        )
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11.2,
            longitude=22.2,
            date_time='2024-10-12T14:42:15.123456',

        )
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11.1,
            longitude=22.1,
            date_time='2024-10-12T14:35:15.123456',

        )

        result = calculate_run_time_in_seconds(self.run_in_progress)
        self.assertEqual(result, 720)

    def test_run_endpoint_run_time_seconds_field(self):
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11,
            longitude=22,
            date_time='2024-10-12T14:30:15.123456',

        )
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11.1,
            longitude=22.1,
            date_time='2024-10-12T14:31:15.123456',

        )
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11.2,
            longitude=22.2,
            date_time='2024-10-12T14:42:15.123456',

        )
        Positions.objects.create(
            run=self.run_in_progress,
            latitude=11.1,
            longitude=22.1,
            date_time='2024-10-12T14:35:15.123456',

        )

        response = self.client.post(reverse('run-stop', args=[self.run_in_progress.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('runs-detail', args=[self.run_in_progress.id]))
        self.assertIn('run_time_seconds', response.json())
        self.assertEqual(response.json().get('run_time_seconds'), 720)
