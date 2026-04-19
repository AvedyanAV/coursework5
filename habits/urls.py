from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'habits'

# Создаем router для ViewSet
router = DefaultRouter()
router.register(r'habits', views.HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    path('habits/public/', views.PublicHabitList.as_view(), name='public-habits'),
]
