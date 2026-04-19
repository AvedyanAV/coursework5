from celery.schedules import crontab

# Расписание периодических задач
CELERY_BEAT_SCHEDULE = {
    # 1. Проверка привычек каждый час
    'check-habits-every-hour': {
        'task': 'tg_bot.tasks.check_habits_reminders',
        'schedule': crontab(minute=0, hour='*'),  # Каждый час в 00 минут
        'options': {
            'expires': 3600,  # Задача актуальна 1 час
        }
    },

    # 2. Утренний дайджест в 8:00
    'morning-digest-8am': {
        'task': 'tg_bot.tasks.send_morning_digest',
        'schedule': crontab(minute=0, hour=8),  # В 8:00 каждый день
        'options': {
            'expires': 3600,
        }
    },

    # 3. Вечерний дайджест в 20:00
    'evening-digest-8pm': {
        'task': 'tg_bot.tasks.send_evening_digest',
        'schedule': crontab(minute=0, hour=20),  # В 20:00 каждый день
    },

    # 4. Обновление серий в полночь
    'update-streaks-midnight': {
        'task': 'habits.tasks.update_habit_streaks',
        'schedule': crontab(minute=0, hour=0),  # В полночь
    },

    # 5. Очистка старых уведомлений раз в неделю
    'cleanup-old-notifications': {
        'task': 'tg_bot.tasks.cleanup_old_notifications',
        'schedule': crontab(minute=0, hour=3, day_of_week=0),  # Воскресенье, 3:00
    },

    # 6. Отправка отчета каждую пятницу в 10:00
    'weekly-report-friday': {
        'task': 'habits.tasks.send_weekly_report',
        'schedule': crontab(minute=0, hour=10, day_of_week=4),  # Пятница, 10:00
    },

    # 7. Проверка невыполненных привычек в 21:00
    'check-missed-habits': {
        'task': 'habits.tasks.check_missed_habits',
        'schedule': crontab(minute=0, hour=21),  # В 21:00 каждый день
    },
}
