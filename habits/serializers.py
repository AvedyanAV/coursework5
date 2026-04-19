from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',)

    def validate(self, data):
        """Валидация для привычек"""
        # Проверка: нельзя одновременно related_habit и reward
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError(
                "Нельзя одновременно указать связанную привычку и вознаграждение"
            )

        # Проверка: время выполнения не больше 120 секунд
        if data.get('duration_seconds', 0) > 120:
            raise serializers.ValidationError(
                "Время выполнения не должно превышать 120 секунд"
            )

        # Проверка: у приятной привычки не может быть reward или related_habit
        if data.get('is_pleasant'):
            if data.get('reward') or data.get('related_habit'):
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки"
                )

        # Проверка: периодичность от 1 до 7 дней
        periodicity = data.get('periodicity', 1)
        if periodicity < 1 or periodicity > 7:
            raise serializers.ValidationError(
                "Периодичность должна быть от 1 до 7 дней"
            )

        return data
