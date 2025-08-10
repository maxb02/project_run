from django.db import models
from django.contrib.auth import get_user_model


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'init', 'Init'
        IN_PROGRESS = 'in_progress', 'In Progress'
        FINISHED = 'finished', 'Finished'

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(choices=Status.choices, max_length=11, default=Status.INIT)
