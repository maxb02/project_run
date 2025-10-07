from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from app_run.validators import latitude_validator, longitude_validator

User = get_user_model()


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'init', 'Init'
        IN_PROGRESS = 'in_progress', 'In Progress'
        FINISHED = 'finished', 'Finished'

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(choices=Status.choices, max_length=11, default=Status.INIT)
    distance = models.FloatField(blank=True, null=True)
    run_time_seconds = models.PositiveIntegerField(blank=True, null=True)
    speed = models.FloatField(null=True, blank=True)


class AthleteInfo(models.Model):
    athlete = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_info')
    weight = models.PositiveSmallIntegerField(null=True, blank=True,
                                              validators=[
                                                  MinValueValidator(1),
                                                  MaxValueValidator(899)])
    goals = models.CharField(max_length=140, null=True, blank=True)


class Challenge(models.Model):
    class NameChoices(models.TextChoices):
        RUN10 = 'run10', 'Сделай 10 Забегов!'
        RUN50KM = 'run50km', 'Пробеги 50 километров!'
        RUN2KMIN10M = 'run2kmin10m', '2 километра за 10 минут!'

    full_name = models.CharField(max_length=55, choices=NameChoices.choices, default=NameChoices.RUN10)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenges')


class Positions(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='positions')
    latitude = models.FloatField(validators=[latitude_validator])
    longitude = models.FloatField(validators=[longitude_validator])
    date_time = models.DateTimeField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)


class CollectibleItem(models.Model):
    name = models.CharField(max_length=140)
    uid = models.CharField(max_length=140)
    latitude = models.FloatField(validators=[latitude_validator])
    longitude = models.FloatField(validators=[longitude_validator])
    picture = models.URLField()
    value = models.IntegerField()
    user = models.ManyToManyField(User, related_name='collectible_items', )


class Subscribe(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', null=True, blank=True)
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers', null=True, blank=True)

    class Meta:
        unique_together = ('subscriber', 'subscribed_to')
