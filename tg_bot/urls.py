from django.urls import path
from . import views

app_name = 'tg_bot'

urlpatterns = [
    path('webhook/', views.TelegramWebhookView.as_view(), name='webhook'),
    path('webhook-simple/', views.telegram_webhook, name='webhook-simple'),
]
