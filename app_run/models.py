from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'init', 'Init'
        IN_PROGRESS = 'in_progress', 'In Progress'
        FINISHED = 'finished', 'Finished'

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(choices=Status.choices, max_length=11, default=Status.INIT)


class AthleteInfo(models.Model):
    athlete = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='athlete_info')
    weight = models.PositiveSmallIntegerField(null=True, blank=True,
                                              validators=[
                                                  MinValueValidator(1),
                                                  MaxValueValidator(899)])
    goals = models.CharField(max_length=140, null=True, blank=True)


class Challenge(models.Model):
    class NameChoices(models.TextChoices):
        RUN10 = 'run10', 'Сделай 10 Забегов!'

    full_name = models.CharField(max_length=55, choices=NameChoices.choices, default=NameChoices.RUN10)
    athlete = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='challenges')
