from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор с полной валидацией"""

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('id', 'user', 'execution_count', 'streak_days')

    def validate_duration_seconds(self, value):
        """Валидация времени выполнения"""
        if value > 120:
            raise serializers.ValidationError(
                f"Время выполнения не должно превышать 120 секунд. "
                f"Вы указали {value} секунд."
            )
        if value < 1:
            raise serializers.ValidationError(
                "Время выполнения должно быть положительным числом."
            )
        return value

    def validate_periodicity(self, value):
        """Валидация периодичности"""
        if value < 1 or value > 7:
            raise serializers.ValidationError(
                f"Периодичность должна быть от 1 до 7 дней. "
                f"Вы указали {value} дней."
            )
        return value

    def validate_action(self, value):
        """Валидация названия действия"""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Название действия должно содержать минимум 3 символа."
            )
        if len(value) > 255:
            raise serializers.ValidationError(
                "Название действия не должно превышать 255 символов."
            )
        return value.strip()

    def validate_place(self, value):
        """Валидация места выполнения"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Место выполнения обязательно для заполнения."
            )
        return value.strip()

    def validate(self, data):
        """
        Валидация на уровне объекта.
        Проверяет взаимосвязи между полями.
        """

        # Правило 1: Исключить одновременный выбор связанной привычки и вознаграждения
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError({
                'non_fields_errors': [
                    "Нельзя одновременно выбрать связанную привычку и указать вознаграждение. "
                    "Выберите что-то одно."
                ]
            })

        # Правило 2: В связанные привычки могут попадать только привычки с признаком приятной привычки
        if data.get('related_habit'):
            related = data.get('related_habit')
            if not related.is_pleasant:
                raise serializers.ValidationError({
                    'related_habit': [
                        f"Привычка '{related.action}' не является приятной. "
                        "Связанная привычка должна иметь признак 'приятная привычка'."
                    ]
                })

        # Правило 3: У приятной привычки не может быть вознаграждения или связанной привычки
        if data.get('is_pleasant'):
            if data.get('reward'):
                raise serializers.ValidationError({
                    'reward': [
                        "У приятной привычки не может быть вознаграждения. "
                        "Приятная привычка сама по себе является вознаграждением."
                    ]
                })
            if data.get('related_habit'):
                raise serializers.ValidationError({
                    'related_habit': [
                        "У приятной привычки не может быть связанной привычки. "
                        "Приятная привычка не может ссылаться на другую привычку."
                    ]
                })

        # Правило 4: Нельзя создавать приятную привычку с duration_seconds > 120
        if data.get('is_pleasant') and data.get('duration_seconds', 0) > 120:
            raise serializers.ValidationError({
                'duration_seconds': [
                    "У приятной привычки время выполнения не должно превышать 120 секунд (2 минуты). "
                    "Приятные привычки должны быть короткими."
                ]
            })

        # Дополнительная проверка: нельзя создать привычку без действия
        if not data.get('action'):
            raise serializers.ValidationError({
                'action': "Действие обязательно для заполнения."
            })

        # Проверка: нельзя создать привычку без времени
        if not data.get('time'):
            raise serializers.ValidationError({
                'time': "Время выполнения обязательно для заполнения."
            })

        return data
