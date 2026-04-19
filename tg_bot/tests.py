from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from tg_bot.utils import TelegramBot
from habits.models import Habit

User = get_user_model()


class TelegramBotTest(TestCase):
    """Тестирование Telegram бота"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            telegram_chat_id='123456789'
        )

        self.habit = Habit.objects.create(
            user=self.user,
            action='Тестовая привычка',
            place='Дом',
            time='10:00:00',
            duration_seconds=60
        )

        self.bot = TelegramBot()

    @patch('requests.post')
    def test_send_message(self, mock_post):
        """Тест отправки сообщения"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response

        result = self.bot.send_message('123456789', 'Test message')

        self.assertIsNotNone(result)
        mock_post.assert_called_once()

    def test_format_habit_message(self):
        """Тест форматирования сообщения"""
        message = self.bot.format_habit_message(self.habit)

        self.assertIn(self.habit.action, message)
        self.assertIn(self.habit.place, message)
        self.assertIn(str(self.habit.duration_seconds), message)

    def test_send_welcome_message(self):
        """Тест приветственного сообщения"""
        with patch.object(self.bot, 'send_message') as mock_send:
            self.bot.send_welcome_message('123456789', 'testuser')
            mock_send.assert_called_once()
