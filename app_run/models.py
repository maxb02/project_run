from django.db import models
from django.contrib.auth import get_user_model


class Run(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
