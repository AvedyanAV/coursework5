import json
import logging
from datetime import timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
from .utils import bot
from habits.models import Habit

User = get_user_model()
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """
    Webhook для получения обновлений от Telegram.
    """

    def post(self, request):
        """Обработка входящих сообщений"""
        try:
            data = json.loads(request.body)
            logger.info(f"Received webhook: {data}")

            # Обрабатываем сообщение
            self.process_update(data)

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JsonResponse({'status': 'error'}, status=500)

    def process_update(self, update):
        """
        Обработка обновления от Telegram.
        """
        # Проверяем, есть ли сообщение
        if 'message' not in update:
            return

        message = update['message']
        chat_id = message['chat']['id']

        # Проверяем, есть ли текст
        if 'text' not in message:
            return

        text = message['text']
        username = message['chat'].get('username', 'User')

        # Обработка команд
        if text == '/start':
            bot.send_welcome_message(chat_id, username)
            self.link_telegram_account(chat_id, username)

        elif text == '/help':
            self.send_help_message(chat_id)

        elif text == '/my_habits':
            self.send_user_habits(chat_id)

        elif text == '/today':
            self.send_today_habits(chat_id)

        else:
            bot.send_message(chat_id, "Неизвестная команда. Используйте /help для списка команд.")

    def link_telegram_account(self, chat_id, username):
        """
        Привязка Telegram аккаунта к пользователю.
        """
        # Ищем пользователя по username
        try:
            user = User.objects.get(username=username)
            user.telegram_chat_id = str(chat_id)
            user.save()
            bot.send_message(chat_id, f"✅ Ваш аккаунт {username} успешно привязан!")
        except User.DoesNotExist:
            bot.send_message(
                chat_id,
                f"❌ Пользователь {username} не найден.\n"
                "Пожалуйста, зарегистрируйтесь в веб-приложении с таким же именем."
            )

    def send_help_message(self, chat_id):
        """Отправка справки"""
        help_text = """
<b>📚 Доступные команды:</b>

/start - Начать работу с ботом
/help - Показать эту справку
/my_habits - Список моих привычек
/today - Привычки на сегодня

<b>💡 Что делать:</b>
1. Зарегистрируйтесь в веб-приложении
2. Создайте привычки
3. Я буду присылать вам напоминания

<b>📞 Поддержка:</b>
При возникновении проблем обращайтесь к администратору.
"""
        bot.send_message(chat_id, help_text)

    def send_user_habits(self, chat_id):
        """Отправка списка привычек пользователя"""
        # Находим пользователя по chat_id
        try:
            user = User.objects.get(telegram_chat_id=str(chat_id))
            habits = Habit.objects.filter(user=user, is_active=True)

            if not habits.exists():
                bot.send_message(chat_id, "У вас пока нет привычек. Создайте их в веб-приложении!")
                return

            message = "<b>📋 Ваши привычки:</b>\n\n"
            for i, habit in enumerate(habits, 1):
                status = "✅" if habit.last_executed and habit.last_executed.date() == timezone.now().date() else "⏳"
                message += f"{i}. {status} {habit.action} - {habit.time.strftime('%H:%M')}\n"

            bot.send_message(chat_id, message)
        except User.DoesNotExist:
            bot.send_message(chat_id, "❌ Аккаунт не привязан. Используйте /start для привязки.")

    def send_today_habits(self, chat_id):
        """Отправка привычек на сегодня"""
        try:
            user = User.objects.get(telegram_chat_id=str(chat_id))
            today = timezone.now().date()

            habits = Habit.objects.filter(
                user=user,
                is_active=True
            ).exclude(
                last_executed__date=today
            )

            if not habits.exists():
                bot.send_message(chat_id, "На сегодня нет запланированных привычек! Отдохните 🎉")
                return

            message = "<b>📅 Привычки на сегодня:</b>\n\n"
            for habit in habits:
                message += f"🎯 {habit.action} в {habit.time.strftime('%H:%M')}\n"
                message += f"   📍 {habit.place}\n\n"

            bot.send_message(chat_id, message)
        except User.DoesNotExist:
            bot.send_message(chat_id, "❌ Аккаунт не привязан. Используйте /start для привязки.")


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """
    Упрощенная версия webhook (функция вместо класса).
    """
    try:
        data = json.loads(request.body)

        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')

            if text == '/start':
                bot.send_welcome_message(chat_id, message['chat'].get('username', 'User'))
            elif text == '/help':
                bot.send_message(chat_id, "Помощь: используйте /start для начала")
            else:
                bot.send_message(chat_id, "Используйте /start для начала работы")

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JsonResponse({'status': 'error'}, status=500)
