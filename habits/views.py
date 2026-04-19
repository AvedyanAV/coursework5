from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import models
from .models import Habit
from .serializers import HabitSerializer, HabitListSerializer
from .permissions import IsOwner
from .pagination import HabitPagination


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с привычками.

    Поддерживаемые действия:
    - GET /api/habits/ - список привычек пользователя
    - POST /api/habits/ - создание привычки
    - GET /api/habits/{id}/ - просмотр привычки
    - PUT /api/habits/{id}/ - редактирование
    - DELETE /api/habits/{id}/ - удаление
    - POST /api/habits/{id}/execute/ - отметить выполнение
    """
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = HabitPagination

    def get_queryset(self):
        """Возвращаем только привычки текущего пользователя"""
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """При создании автоматически подставляем пользователя"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Эндпоинт для отметки выполнения привычки.
        POST /api/habits/{id}/execute/
        """
        habit = self.get_object()
        habit.mark_as_executed()

        return Response({
            'status': 'success',
            'message': f'Привычка "{habit.action}" выполнена!',
            'execution_count': habit.execution_count,
            'streak_days': habit.streak_days
        }, status=status.HTTP_200_OK)


class PublicHabitList(generics.ListAPIView):
    """
    Список публичных привычек.
    GET /api/habits/public/
    Доступно без авторизации.
    """
    serializer_class = HabitListSerializer
    permission_classes = [AllowAny]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True, is_active=True)


class HabitStatisticsView(generics.RetrieveAPIView):
    """
    Статистика по привычкам пользователя.
    GET /api/statistics/
    Только для авторизованных пользователей.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        habits = Habit.objects.filter(user=user)

        total_habits = habits.count()
        completed_today = habits.filter(
            last_executed__date=timezone.now().date()
        ).count()
        public_habits = habits.filter(is_public=True).count()
        pleasant_habits = habits.filter(is_pleasant=True).count()

        max_streak = habits.aggregate(
            max_streak=models.Max('streak_days')
        )['max_streak'] or 0

        completion_rate = round(
            (completed_today / total_habits * 100) if total_habits > 0 else 0, 1
        )

        return Response({
            'total_habits': total_habits,
            'completed_today': completed_today,
            'public_habits': public_habits,
            'pleasant_habits': pleasant_habits,
            'max_streak_days': max_streak,
            'completion_rate': completion_rate
        })
