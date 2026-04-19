import logging
import requests
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from habits.models import Habit
from django.db import models


logger = logging.getLogger(__name__)


@shared_task
def send_telegram_message(chat_id, message):
    """
    Отправка сообщения в Telegram.
    """
    token = settings.TELEGRAM_TOKEN

    if not token:
        logger.warning("TELEGRAM_TOKEN not set")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Message sent to {chat_id}: {message[:50]}...")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        return None


@shared_task
def send_habit_reminder(habit_id):
    """
    Отправка напоминания о конкретной привычке.
    """
    try:
        habit = Habit.objects.get(id=habit_id, is_active=True)
    except Habit.DoesNotExist:
        logger.error(f"Habit {habit_id} not found")
        return None

    if not habit.user.telegram_chat_id:
        logger.error(f"User {habit.user.username} has no Telegram chat ID")
        return None

    message = f"""
🔔 <b>Напоминание о привычке!</b>

<b>Действие:</b> {habit.action}
<b>Место:</b> {habit.place}
<b>Время:</b> {habit.time.strftime('%H:%M')}
<b>Длительность:</b> {habit.duration_seconds} секунд

"""

    if habit.related_habit:
        message += f"<b>Награда:</b> После выполнения - {habit.related_habit.action}\n"
    elif habit.reward:
        message += f"<b>Награда:</b> {habit.reward}\n"

    if habit.streak_days > 0:
        message += f"\n🔥 <b>Серия:</b> {habit.streak_days} дней!"

    message += "\n\n✅ Не забудьте выполнить привычку и отметить её в приложении!"

    return send_telegram_message(habit.user.telegram_chat_id, message)


@shared_task
def check_habits_reminders():
    """
    Проверка привычек и отправка напоминаний.
    """
    now = timezone.now()
    current_time = now.time()
    current_date = now.date()

    habits = Habit.objects.filter(
        is_active=True,
        time__lte=current_time,
        user__telegram_chat_id__isnull=False
    ).exclude(
        last_executed__date=current_date
    )

    sent_count = 0
    for habit in habits:
        send_habit_reminder.delay(habit.id)
        sent_count += 1

    logger.info(f"Sent {sent_count} reminders")
    return f"Sent {sent_count} reminders"


@shared_task
def send_daily_digest():
    """
    Отправка ежедневного дайджеста.
    """
    from django.contrib.auth import get_user_model
    from django.db import models

    User = get_user_model()
    users = User.objects.filter(telegram_chat_id__isnull=False)

    sent_count = 0
    for user in users:
        today = timezone.now().date()
        habits = Habit.objects.filter(
            user=user,
            is_active=True
        ).exclude(
            last_executed__date=today
        )

        if habits.exists():
            message = f"""
🌅 <b>Доброе утро, {user.username}!</b>

Сегодня запланировано <b>{habits.count()}</b> привычек:

"""
            for habit in habits:
                message += f"• <b>{habit.action}</b> в {habit.time.strftime('%H:%M')} ({habit.place})\n"

            # Статистика
            total_completed = habits.aggregate(total=models.Sum('execution_count'))['total'] or 0
            max_streak = habits.aggregate(max_streak=models.Max('streak_days'))['max_streak'] or 0

            message += "\n<b>Статистика:</b>\n"
            message += f"🔥 Максимальная серия: {max_streak} дней\n"
            message += f"✅ Всего выполнений: {total_completed}\n"

            message += "\n✏️ Отмечайте выполнение в приложении!"

            send_telegram_message(user.telegram_chat_id, message)
            sent_count += 1

    return f"Sent daily digest to {sent_count} users"


@shared_task
def send_morning_digest():
    """
    Утренний дайджест в 8:00.
    Отправляет список привычек на сегодня.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.filter(telegram_chat_id__isnull=False)
    today = timezone.now().date()

    sent_count = 0
    for user in users:
        habits = Habit.objects.filter(
            user=user,
            is_active=True
        ).exclude(
            last_executed__date=today
        )

        if habits.exists():
            message = f"""
🌅 <b>Доброе утро, {user.username}!</b>

Сегодня запланировано <b>{habits.count()}</b> привычек:

"""
            for habit in habits:
                message += f"• <b>{habit.action}</b> в {habit.time.strftime('%H:%M')} ({habit.place})\n"

            # Добавляем статистику
            total_completed = Habit.objects.filter(user=user).aggregate(
                total=models.Sum('execution_count')
            )['total'] or 0

            message += "\n📊 <b>Общая статистика:</b>\n"
            message += f"✅ Всего выполнений: {total_completed}\n"

            send_telegram_message(user.telegram_chat_id, message)
            sent_count += 1

    logger.info(f"Morning digest sent to {sent_count} users")
    return f"Sent morning digest to {sent_count} users"


@shared_task
def send_evening_digest():
    """
    Вечерний дайджест в 20:00.
    Отправляет отчет о выполненных привычках за день.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.filter(telegram_chat_id__isnull=False)
    today = timezone.now().date()

    sent_count = 0
    for user in users:
        habits_today = Habit.objects.filter(
            user=user,
            last_executed__date=today
        )
        habits_total = Habit.objects.filter(user=user, is_active=True)

        completed_count = habits_today.count()
        total_count = habits_total.count()

        completion_rate = round((completed_count / total_count * 100) if total_count > 0 else 0, 1)

        message = f"""
🌙 <b>Добрый вечер, {user.username}!</b>

<b>Отчет за сегодня:</b>
✅ Выполнено привычек: {completed_count} из {total_count}
📊 Процент выполнения: {completion_rate}%

"""

        if habits_today.exists():
            message += "<b>Выполненные привычки:</b>\n"
            for habit in habits_today:
                message += f"• {habit.action} ✅\n"

        message += (f"\n🔥 <b>Текущая серия:</b> "
                    f"{habits_total.aggregate(max_streak=models.Max('streak_days'))['max_streak'] or 0} дней")
        message += "\n\nЗавтра новый день! Продолжайте в том же духе! 💪"

        send_telegram_message(user.telegram_chat_id, message)
        sent_count += 1

    return f"Sent evening digest to {sent_count} users"


@shared_task
def cleanup_old_notifications():
    """
    Очистка старых уведомлений (старше 30 дней).
    Запускается раз в неделю.
    """
    from tg_bot.models import NotificationLog

    threshold_date = timezone.now() - timezone.timedelta(days=30)
    deleted_count = NotificationLog.objects.filter(
        created_at__lt=threshold_date
    ).delete()[0]

    logger.info(f"Deleted {deleted_count} old notifications")
    return f"Deleted {deleted_count} old notifications"
