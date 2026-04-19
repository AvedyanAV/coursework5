import logging
from django.contrib.auth import get_user_model
from .utils import bot

User = get_user_model()
logger = logging.getLogger(__name__)


def handle_message(update):
    """Обработка входящих сообщений"""

    if 'message' not in update:
        return

    message = update['message']
    chat_id = message['chat']['id']

    if 'text' not in message:
        bot.send_message(chat_id, "Пожалуйста, отправьте текстовое сообщение")
        return

    text = message['text']
    username = message['chat'].get('username', message['chat'].get('first_name', 'User'))

    if text == '/start':
        handle_start(chat_id, username)
    elif text == '/help':
        handle_help(chat_id)
    elif text == '/my_habits':
        handle_my_habits(chat_id)
    elif text == '/today':
        handle_today_habits(chat_id)
    else:
        bot.send_message(chat_id, "Неизвестная команда. Используйте /help")


def handle_start(chat_id, username):
    """Обработка команды /start"""

    # Привязываем Telegram аккаунт
    try:
        user = User.objects.get(username=username)
        user.telegram_chat_id = str(chat_id)
        user.save()

        message = f"""
👋 <b>Добро пожаловать, {username}!</b>

✅ Ваш аккаунт успешно привязан!

Я буду присылать вам напоминания о привычках.

<b>Команды:</b>
/help - Помощь
/my_habits - Мои привычки
/today - Привычки на сегодня
"""
        bot.send_message(chat_id, message)

    except User.DoesNotExist:
        message = f"""
❌ <b>Пользователь {username} не найден!</b>

Пожалуйста, зарегистрируйтесь в веб-приложении:
http://localhost:8000/api/register/

Используйте то же имя пользователя: <b>{username}</b>

После регистрации отправьте /start снова.
"""
        bot.send_message(chat_id, message)


def handle_help(chat_id):
    """Обработка команды /help"""
    message = """
<b>📚 Доступные команды:</b>

/start - Начать работу и привязать аккаунт
/help - Показать эту справку
/my_habits - Список моих привычек
/today - Привычки на сегодня

<b>💡 О боте:</b>
Я буду присылать вам напоминания о привычках
в указанное время.

<b>📞 Поддержка:</b>
При возникновении проблем обращайтесь к администратору.
"""
    bot.send_message(chat_id, message)


def handle_my_habits(chat_id):
    """Обработка команды /my_habits"""
    try:
        user = User.objects.get(telegram_chat_id=str(chat_id))
        from habits.models import Habit
        from django.utils import timezone

        habits = Habit.objects.filter(user=user, is_active=True)

        if not habits.exists():
            bot.send_message(chat_id, "У вас пока нет привычек. Создайте их в веб-приложении!")
            return

        message = "<b>📋 Ваши привычки:</b>\n\n"
        today = timezone.now().date()

        for i, habit in enumerate(habits, 1):
            is_completed_today = habit.last_executed and habit.last_executed.date() == today
            status = "✅" if is_completed_today else "⏳"
            message += f"{i}. {status} {habit.action}\n"
            message += f"   ⏰ {habit.time.strftime('%H:%M')} | 📍 {habit.place}\n"

            if habit.streak_days > 0:
                message += f"   🔥 Серия: {habit.streak_days} дней\n"
            message += "\n"

        bot.send_message(chat_id, message)

    except User.DoesNotExist:
        bot.send_message(chat_id, "❌ Аккаунт не привязан. Используйте /start для привязки.")


def handle_today_habits(chat_id):
    """Обработка команды /today"""
    try:
        user = User.objects.get(telegram_chat_id=str(chat_id))
        from habits.models import Habit
        from django.utils import timezone

        today = timezone.now().date()
        current_time = timezone.now().time()

        habits = Habit.objects.filter(
            user=user,
            is_active=True
        ).exclude(
            last_executed__date=today
        )

        if not habits.exists():
            bot.send_message(chat_id, "На сегодня нет запланированных привычек! 🎉")
            return

        message = "<b>📅 Привычки на сегодня:</b>\n\n"

        for habit in habits:
            is_past = habit.time < current_time
            status = "🔴" if is_past else "🟢"
            message += f"{status} <b>{habit.action}</b>\n"
            message += f"   ⏰ {habit.time.strftime('%H:%M')} | 📍 {habit.place}\n\n"

        bot.send_message(chat_id, message)

    except User.DoesNotExist:
        bot.send_message(chat_id, "❌ Аккаунт не привязан. Используйте /start для привязки.")
