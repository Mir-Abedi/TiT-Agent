from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Starts telegram bot.'

    def add_arguments(self, parser):
        # Optional: define arguments
        parser.add_argument(
            '--name',
            type=str,
            help='Name to greet'
        )

    def handle(self, *args, **options):
        name = options.get('name') or 'World'
        self.stdout.write(self.style.SUCCESS(f'Hello, {name}!'))