from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Habit(models.Model):
    """
    Модель привычки на основе книги "Атомные привычки".
    """

    # Связь с пользователем
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name="Пользователь",
        help_text="Владелец привычки"
    )

    # Основные поля
    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку",
        db_index=True
    )

    time = models.TimeField(
        verbose_name="Время",
        help_text="Время, когда необходимо выполнять привычку",
        db_index=True
    )

    action = models.CharField(
        max_length=255,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка"
    )

    # Типы привычек
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Приятная привычка",
        help_text="Отмечает, является ли привычка приятной (вознаграждением)"
    )

    # Связанная привычка (только для полезных привычек)
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой (для полезных привычек)",
        related_name='related_to'
    )

    # Периодичность выполнения
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name="Периодичность (дни)",
        help_text="Периодичность выполнения привычки (от 1 до 7 дней)"
    )

    # Вознаграждение
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Чем пользователь должен себя вознаградить после выполнения"
    )

    # Время на выполнение
    duration_seconds = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        default=120,
        verbose_name="Время на выполнение (секунды)",
        help_text="Время, которое пользователь потратит на выполнение (не более 120 секунд)"
    )

    # Публичность
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
        help_text="Можно публиковать в общий доступ для других пользователей",
        db_index=True
    )

    # Дополнительные поля для отслеживания
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text="Активна ли привычка в данный момент"
    )

    last_executed = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Последнее выполнение",
        help_text="Дата и время последнего выполнения привычки"
    )

    execution_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество выполнений",
        help_text="Общее количество выполнений привычки"
    )

    streak_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Серия (дни)",
        help_text="Количество дней подряд выполнения привычки"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['time', 'place']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'is_public']),
            models.Index(fields=['time', 'periodicity']),
            models.Index(fields=['user', 'last_executed']),
        ]

    def __str__(self):
        return f"{self.action} в {self.time} в {self.place}"

    def clean(self):
        """Валидация на уровне модели"""
        from django.core.exceptions import ValidationError

        # 1. Нельзя одновременно заполнить related_habit и reward
        if self.related_habit and self.reward:
            raise ValidationError(
                "Нельзя одновременно выбрать связанную привычку и указать вознаграждение"
            )

        # 2. Связанная привычка может быть только приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка должна иметь признак 'приятная привычка'"
            )

        # 3. У приятной привычки не может быть reward или related_habit
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки"
            )

        # 4. Время выполнения не должно превышать 120 секунд
        if self.duration_seconds > 120:
            raise ValidationError(
                "Время выполнения не должно превышать 120 секунд"
            )

        # 5. Периодичность должна быть от 1 до 7 дней
        if not (1 <= self.periodicity <= 7):
            raise ValidationError(
                "Периодичность должна быть от 1 до 7 дней"
            )

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)

    def mark_as_executed(self):
        """Отметить привычку как выполненную"""
        now = timezone.now()
        self.last_executed = now
        self.execution_count += 1

        # Обновляем серию (streak)
        if self.last_executed:
            days_since_last = (now - self.last_executed).days
            if days_since_last <= self.periodicity:
                self.streak_days += 1
            else:
                self.streak_days = 1

        self.save(update_fields=['last_executed', 'execution_count', 'streak_days'])

        # Обновляем счетчик у пользователя
        self.user.increment_habits_count()

    def is_due(self):
        """Проверяет, пора ли выполнять привычку"""
        if not self.last_executed:
            return True

        days_since_last = (timezone.now() - self.last_executed).days
        return days_since_last >= self.periodicity

    @property
    def duration_minutes(self):
        """Время выполнения в минутах"""
        return self.duration_seconds // 60

    @property
    def duration_display(self):
        """Человекочитаемое время выполнения"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        if minutes > 0:
            return f"{minutes} мин {seconds} сек"
        return f"{seconds} сек"


class HabitExecution(models.Model):
    """
    Модель для хранения истории выполнения привычек.
    """

    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name="Привычка"
    )

    executed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время выполнения"
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Заметки"
    )

    class Meta:
        verbose_name = "Выполнение привычки"
        verbose_name_plural = "Выполнения привычек"
        ordering = ['-executed_at']

    def __str__(self):
        return f"{self.habit.action} - {self.executed_at}"
