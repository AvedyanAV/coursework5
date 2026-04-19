from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'habits', views.HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    # Убедитесь, что URL правильный
    path('public-habits/', views.PublicHabitList.as_view(), name='public-habits'),
    path('statistics/', views.HabitStatisticsView.as_view(), name='statistics'),
]
