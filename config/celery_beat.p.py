from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Проверка привычек каждый час
    'check-habits-every-hour': {
        'task': 'tg_bot.tasks.check_habits_reminders',
        'schedule': crontab(minute=0, hour='*'),  # Каждый час в 00 минут
    },

    # Утренний дайджест в 8:00
    'morning-digest': {
        'task': 'tg_bot.tasks.send_morning_digest',
        'schedule': crontab(minute=0, hour=8),  # В 8:00 каждый день
    },

    # Обновление серий в полночь
    'update-streaks-midnight': {
        'task': 'habits.tasks.update_habit_streaks',
        'schedule': crontab(minute=0, hour=0),  # В полночь
    },
}
