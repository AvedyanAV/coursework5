from django.db import models
from django.conf import settings


class NotificationLog(models.Model):
    """
    Модель для логирования отправленных уведомлений.
    """

    NOTIFICATION_STATUS = [
        ('pending', 'Ожидает отправки'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Пользователь"
    )

    habit = models.ForeignKey(
        'habits.Habit',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Привычка",
        null=True,
        blank=True
    )

    message = models.TextField(
        verbose_name="Текст уведомления"
    )

    status = models.CharField(
        max_length=20,
        choices=NOTIFICATION_STATUS,
        default='pending',
        verbose_name="Статус"
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ошибка"
    )

    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Время отправки"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано"
    )

    class Meta:
        verbose_name = "Лог уведомления"
        verbose_name_plural = "Логи уведомлений"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Уведомление для {self.user.username} - {self.status}"
