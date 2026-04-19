# habits/models.py
from django.db import models
from django.conf import settings


class Habit(models.Model):
    """Модель привычки (временная версия)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits'
    )
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    periodicity = models.PositiveSmallIntegerField(default=1)
    reward = models.CharField(max_length=255, blank=True, null=True)
    duration_seconds = models.PositiveSmallIntegerField(default=120)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.action} в {self.time}"