from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum, Min, Max
from geopy.distance import geodesic

from .models import Challenge, Run, Positions, CollectibleItem


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


def calculate_run_distance(run_id):
    positions = Positions.objects.filter(run_id=run_id).order_by('id').values_list('latitude', 'longitude')

    total_distance = sum(
        geodesic(positions[i], positions[i + 1]).kilometers
        for i in range(len(positions) - 1)
    )
    Run.objects.filter(id=run_id).update(distance=total_distance)
    return total_distance


def collect_item_if_nearby(latitude, longitude, user):
    collected_items = []
    for item in CollectibleItem.objects.exclude(user=user):
        try:
            distance = geodesic((latitude, longitude), (item.latitude, item.longitude)).meters
        except ValueError:
            continue
        if distance <= 100:
            collected_items.append(item)
    user.collectible_items.add(*collected_items)
    return collected_items


def calculate_run_time_in_seconds(run):
    result = run.positions.aggregate(min_date=Min("date_time"),
                                     max_date=Max("date_time"),
                                     )
    if result['min_date'] and result['max_date']:
        return int((result['max_date'] - result['min_date']).total_seconds())
    return None


def calculate_distance_for_previous_position(previous_position, latitude, longitude):
    if previous_position:
        distance_to_previous = round(geodesic((latitude, longitude),
                                              (previous_position.latitude, previous_position.longitude)).meters, 2)
        if previous_position.distance:
            return previous_position.distance + distance_to_previous
        return distance_to_previous
    return None
