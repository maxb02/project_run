from .models import Challenge
from django.contrib.auth import get_user_model

def award_challenge_if_completed(athlete_id):
    user = get_user_model().objects.get(id=athlete_id)
    if user.runs.count() == 10:
        return Challenge.objects.create(athlete_id=athlete_id, full_name=Challenge.NameChoices.RUN10)

    return None
