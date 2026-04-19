from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Расширяет стандартную модель Django дополнительными полями.
    """

    # Дополнительные поля для трекера привычек
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=False,
        verbose_name="Telegram Chat ID",
        help_text="ID чата пользователя в Telegram для отправки уведомлений"
    )

    # Поле для хранения времени последнего уведомления
    last_notification_sent = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Последнее уведомление",
        help_text="Время последнего отправленного уведомления"
    )

    # Статистика использования
    total_habits_created = models.PositiveIntegerField(
        default=0,
        verbose_name="Всего привычек создано"
    )

    # Дата и время последней активности
    last_active = models.DateTimeField(
        auto_now=True,
        verbose_name="Последняя активность"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['telegram_chat_id']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """Переопределяем save для обновления статистики"""
        if not self.pk:
            pass
        super().save(*args, **kwargs)

    def increment_habits_count(self):
        """Увеличивает счетчик созданных привычек"""
        self.total_habits_created += 1
        self.save(update_fields=['total_habits_created'])
