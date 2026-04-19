from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Кастомная админка для пользователя"""

    list_display = ('username', 'email', 'first_name', 'last_name', 'telegram_chat_id')
    fieldsets = UserAdmin.fieldsets + (
        ('Telegram', {'fields': ('telegram_chat_id',)}),
    )
