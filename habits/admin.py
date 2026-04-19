from django.contrib import admin
from .models import Habit, HabitExecution


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'time', 'place', 'is_public', 'is_active', 'streak_days')
    list_filter = ('is_public', 'is_active', 'is_pleasant', 'periodicity')
    search_fields = ('action', 'place', 'user__username')
    readonly_fields = ('execution_count', 'streak_days', 'created_at', 'updated_at')

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time')
        }),
        ('Тип привычки', {
            'fields': ('is_pleasant', 'related_habit', 'reward')
        }),
        ('Настройки выполнения', {
            'fields': ('periodicity', 'duration_seconds')
        }),
        ('Дополнительно', {
            'fields': ('is_public', 'is_active')
        }),
        ('Статистика', {
            'fields': ('execution_count', 'streak_days', 'last_executed'),
            'classes': ('collapse',)
        }),
        ('Системные поля', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HabitExecution)
class HabitExecutionAdmin(admin.ModelAdmin):
    list_display = ('habit', 'executed_at', 'notes')
    list_filter = ('executed_at',)
    search_fields = ('habit__action', 'notes')
    readonly_fields = ('executed_at',)
