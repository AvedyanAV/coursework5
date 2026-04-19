import time
import logging
from django.core.management.base import BaseCommand
from tg_bot.utils import bot
from tg_bot.handlers import handle_message

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Запуск Telegram бота в режиме polling"""

    help = 'Run Telegram bot in polling mode'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot (polling mode)...'))

        import requests
        last_update_id = 0

        while True:
            try:
                url = f"{bot.api_url}/getUpdates"
                params = {'offset': last_update_id + 1, 'timeout': 30}

                response = requests.get(url, params=params, timeout=35)
                data = response.json()

                if data.get('ok'):
                    for update in data.get('result', []):
                        last_update_id = update['update_id']
                        handle_message(update)

                time.sleep(1)

            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)
