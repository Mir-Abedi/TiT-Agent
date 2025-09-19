from django.core.management.base import BaseCommand
from telegram.tasks import get_telegram_app

class Command(BaseCommand):
    help = 'Starts telegram bot.'

    def handle(self, *args, **options):
        get_telegram_app().start()