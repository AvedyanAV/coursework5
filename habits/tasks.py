from celery import shared_task
from django.utils import timezone
from .models import Habit


@shared_task
def update_habit_streaks():
    """
    Обновление серий выполнения привычек.
    Запускается ежедневно в полночь.
    """
    habits = Habit.objects.filter(is_active=True)

    for habit in habits:
        if habit.last_executed:
            days_since = (timezone.now().date() - habit.last_executed.date()).days
            if days_since > habit.periodicity:
                # Серия прервана
                habit.streak_days = 0
                habit.save(update_fields=['streak_days'])

    return f"Updated streaks for {habits.count()} habits"


@shared_task
def check_missed_habits():
    """
    Проверка невыполненных привычек за день.
    Отправляет напоминания о пропущенных привычках.
    """
    from django.contrib.auth import get_user_model
    from tg_bot.tasks import send_telegram_message

    User = get_user_model()
    today = timezone.now().date()

    users = User.objects.filter(telegram_chat_id__isnull=False)
    notified_count = 0

    for user in users:
        missed_habits = Habit.objects.filter(
            user=user,
            is_active=True
        ).exclude(
            last_executed__date=today
        )

        if missed_habits.exists():
            message = f"""
⚠️ <b>Напоминание, {user.username}!</b>

Вы не выполнили сегодня <b>{missed_habits.count()}</b> привычек:

"""
            for habit in missed_habits:
                message += f"• {habit.action} (было запланировано на {habit.time.strftime('%H:%M')})\n"

            message += "\nНе откладывайте на завтра! Выполните привычки прямо сейчас! 💪"

            send_telegram_message(user.telegram_chat_id, message)
            notified_count += 1

    return f"Notified {notified_count} users about missed habits"


@shared_task
def send_weekly_report():
    """
    Отправка еженедельного отчета по пятницам.
    """
    from django.contrib.auth import get_user_model
    from django.db import models
    from tg_bot.tasks import send_telegram_message

    User = get_user_model()
    week_ago = timezone.now() - timezone.timedelta(days=7)

    users = User.objects.filter(telegram_chat_id__isnull=False)
    sent_count = 0

    for user in users:
        habits = Habit.objects.filter(user=user)

        # Статистика за неделю
        total_habits = habits.count()
        total_executions = habits.aggregate(total=models.Sum('execution_count'))['total'] or 0
        avg_streak = habits.aggregate(avg=models.Avg('streak_days'))['avg'] or 0
        max_streak = habits.aggregate(max=models.Max('streak_days'))['max'] or 0

        # Новые привычки за неделю
        new_habits = habits.filter(created_at__gte=week_ago).count()

        message = f"""
📊 <b>Еженедельный отчет</b>

<b>Пользователь:</b> {user.username}
<b>Период:</b> {week_ago.strftime('%d.%m.%Y')} - {timezone.now().strftime('%d.%m.%Y')}

<b>Статистика:</b>
📌 Всего привычек: {total_habits}
✅ Всего выполнений: {total_executions}
🔥 Средняя серия: {avg_streak:.1f} дней
🏆 Максимальная серия: {max_streak} дней
🆕 Новых привычек: {new_habits}

<b>Совет:</b>
Продолжайте в том же темпе! Маленькие шаги каждый день приводят к большим результатам! 🚀
"""

        send_telegram_message(user.telegram_chat_id, message)
        sent_count += 1

    return f"Sent weekly report to {sent_count} users"
