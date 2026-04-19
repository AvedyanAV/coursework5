from django.core.management.base import BaseCommand
from tg_bot.utils import bot


class Command(BaseCommand):
    """Установка webhook для Telegram бота"""

    help = 'Set Telegram webhook'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Webhook URL (e.g., https://your-domain.com/telegram/webhook/)'
        )

    def handle(self, *args, **options):
        url = options.get('url')

        if not url:
            # Для локальной разработки используем ngrok
            self.stdout.write(self.style.WARNING(
                'No URL provided. For local development, use ngrok:\n'
                'ngrok http 8000\n'
                'Then run: python manage.py set_webhook --url https://your-ngrok-url/telegram/webhook/'
            ))
            return

        result = bot.set_webhook(url)

        if result and result.get('ok'):
            self.stdout.write(self.style.SUCCESS(f'Webhook set successfully: {url}'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to set webhook: {result}'))
