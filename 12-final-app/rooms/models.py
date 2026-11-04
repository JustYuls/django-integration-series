from django.db import models


class Room(models.Model):
    """A bookable room. This app knows nothing about bookings: the dependency points the other way."""

    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    has_projector = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
