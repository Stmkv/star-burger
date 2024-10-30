from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField("Адрес", max_length=200, unique=True)
    longitude = models.DecimalField(
        "Долгота", max_digits=13, decimal_places=11, null=True, blank=True
    )
    latitude = models.DecimalField(
        "Широта", max_digits=12, decimal_places=10, null=True, blank=True
    )
    create_date = models.DateTimeField(default=timezone.now)
