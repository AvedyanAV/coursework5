from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Полный сериализатор для привычек"""

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('id', 'user', 'execution_count', 'streak_days', 'created_at', 'updated_at')

    def create(self, validated_data):
        """Создание привычки с привязкой к пользователю"""
        # Получаем user из контекста request
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        else:
            # Если request нет, используем user из context (для тестов)
            user = self.context.get('user')
            if user:
                validated_data['user'] = user
        return super().create(validated_data)

    def validate_duration_seconds(self, value):
        if value > 120:
            raise serializers.ValidationError("Время выполнения не должно превышать 120 секунд")
        return value

    def validate_periodicity(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError("Периодичность должна быть от 1 до 7 дней")
        return value

    def validate(self, data):
        # Нельзя одновременно reward и related_habit
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError({
                'non_field_errors': "Нельзя одновременно указать связанную привычку и вознаграждение"
            })

        # Связанная привычка должна быть приятной
        if data.get('related_habit') and not data.get('related_habit').is_pleasant:
            raise serializers.ValidationError({
                'related_habit': "Связанная привычка должна быть приятной"
            })

        # У приятной привычки не может быть reward или related_habit
        if data.get('is_pleasant'):
            if data.get('reward'):
                raise serializers.ValidationError({
                    'reward': "У приятной привычки не может быть вознаграждения"
                })
            if data.get('related_habit'):
                raise serializers.ValidationError({
                    'related_habit': "У приятной привычки не может быть связанной привычки"
                })

        return data


class HabitListSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор для списков"""

    class Meta:
        model = Habit
        fields = ('id', 'action', 'place', 'time', 'is_pleasant', 'is_public', 'streak_days')
