import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Класс для работы с Telegram API"""

    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, text, parse_mode='HTML'):
        """
        Отправка текстового сообщения.

        Args:
            chat_id: ID чата в Telegram
            text: Текст сообщения
            parse_mode: Форматирование ('HTML' или 'Markdown')

        Returns:
            dict: Ответ от Telegram API
        """
        url = f"{self.api_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Message sent to {chat_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None

    def send_habit_reminder(self, chat_id, habit):
        """
        Отправка напоминания о привычке.

        Args:
            chat_id: ID чата пользователя
            habit: Объект привычки
        """
        message = self.format_habit_message(habit)
        return self.send_message(chat_id, message)

    def format_habit_message(self, habit):
        """
        Форматирование сообщения о привычке.
        """
        emoji = "🎯" if not habit.is_pleasant else "😊"

        message = f"""
{emoji} <b>Напоминание о привычке!</b>

<b>Действие:</b> {habit.action}
<b>Место:</b> {habit.place}
<b>Время:</b> {habit.time.strftime('%H:%M')}
<b>Длительность:</b> {habit.duration_seconds} сек

"""

        if habit.related_habit:
            message += f"<b>Награда:</b> После выполнения - {habit.related_habit.action}\n"
        elif habit.reward:
            message += f"<b>Награда:</b> {habit.reward}\n"

        if habit.streak_days > 0:
            message += f"\n🔥 <b>Серия:</b> {habit.streak_days} дней!"

        message += "\n✅ Отметьте выполнение в приложении!"

        return message

    def send_welcome_message(self, chat_id, username):
        """
        Приветственное сообщение при старте.
        """
        message = f"""
👋 <b>Добро пожаловать, {username}!</b>

Я бот для отслеживания полезных привычек.
Я буду напоминать вам о привычках, которые вы создали в приложении.

<b>Что нужно сделать:</b>
1. Зарегистрируйтесь в веб-приложении
2. Создайте привычки
3. Я буду присылать вам напоминания

<b>Команды:</b>
/start - Показать это сообщение
/help - Помощь
/my_habits - Мои привычки (скоро)
/today - Привычки на сегодня (скоро)

Успехов в формировании полезных привычек! 🚀
"""
        return self.send_message(chat_id, message)

    def set_webhook(self, webhook_url):
        """
        Установка webhook для получения обновлений.
        """
        url = f"{self.api_url}/setWebhook"
        payload = {'url': webhook_url}

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return None

    def delete_webhook(self):
        """
        Удаление webhook.
        """
        url = f"{self.api_url}/deleteWebhook"

        try:
            response = requests.post(url, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return None


# Создаем глобальный экземпляр бота
bot = TelegramBot()
