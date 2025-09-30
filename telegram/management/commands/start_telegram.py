from django.core.management.base import BaseCommand
import os
from telegram.tasks import get_telegram_app

class Command(BaseCommand):
    help = 'Starts telegram bot.'

    def handle(self, *args, **options):
        print(os.getenv("TELEGRAM_BOT_TOKEN"))
        get_telegram_app().run()