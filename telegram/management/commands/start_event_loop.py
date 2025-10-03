from django.core.management.base import BaseCommand
import os
from telegram.tasks import infinite_send_loop

class Command(BaseCommand):
    help = 'Starts telegram bot sending event loop.'

    def handle(self, *args, **options):
        print(os.getenv("TELEGRAM_BOT_TOKEN"))
        print("Starting telegram event loop")
        infinite_send_loop()