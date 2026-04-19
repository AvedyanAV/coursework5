from django.core.management.base import BaseCommand
from tg_bot.utils import bot


class Command(BaseCommand):
    """Удаление webhook Telegram бота"""

    help = 'Delete Telegram webhook'

    def handle(self, *args, **options):
        result = bot.delete_webhook()

        if result and result.get('ok'):
            self.stdout.write(self.style.SUCCESS('Webhook deleted successfully'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to delete webhook: {result}'))
