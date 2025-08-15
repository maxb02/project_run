from .models import Challenge


def award_challenge_if_completed(user):
    if user.object.runs.count() == 10:
        return Challenge.objects.create(athlete=user, full_name=Challenge.NameChoices.RUN10)

    return None
