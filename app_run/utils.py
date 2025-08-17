from django.db.models.aggregates import Sum

from .models import Challenge, Run, Positions
from django.contrib.auth import get_user_model
from geopy.distance import geodesic


def award_challenge_if_completed_run_10(athlete_id):
    user = get_user_model().objects.get(id=athlete_id)

    if user.runs.filter(status=Run.Status.FINISHED).count() == 10:
        return Challenge.objects.create(athlete_id=athlete_id, full_name=Challenge.NameChoices.RUN10)
    return None


def award_challenge_if_completed_run_50km(athlete_id):
    user = get_user_model().objects.get(id=athlete_id)
    if (not user.challenges.filter(full_name=Challenge.NameChoices.RUN50KM).exists() and
            user.runs.aggregate(Sum('distance'))['distance__sum'] >= 50):
        return Challenge.objects.create(athlete_id=athlete_id, full_name=Challenge.NameChoices.RUN50KM)
    return None


def calculate_distance(run_id):
    positions = Positions.objects.filter(run_id=run_id).order_by('id').values_list('latitude', 'longitude')

    total_distance = sum(
        geodesic(positions[i], positions[i + 1]).kilometers
        for i in range(len(positions) - 1)
    )
    Run.objects.filter(id=run_id).update(distance=total_distance)
    return total_distance
