from django.contrib import admin
from . import models

admin.site.register(models.Run)
admin.site.register(models.Challenge)
admin.site.register(models.Positions)
admin.site.register(models.CollectibleItem)
