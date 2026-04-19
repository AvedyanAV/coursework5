from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPagination


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с привычками"""
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Habit.objects.filter(user=user)
        return Habit.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitList(generics.ListAPIView):
    """Список публичных привычек"""
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
