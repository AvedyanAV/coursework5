from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'telegram_chat_id', 'total_habits_created', 'last_active')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'telegram_chat_id')

    fieldsets = UserAdmin.fieldsets + (
        ('Telegram', {
            'fields': ('telegram_chat_id', 'last_notification_sent'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('total_habits_created', 'last_active'),
            'classes': ('collapse',)
        }),
    )
