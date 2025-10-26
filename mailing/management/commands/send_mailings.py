from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = 'Автоматическая отправка активных рассылок'

    def handle(self, *args, **options):

        active_mailings = Mailing.objects.filter(
            status__in=['created', 'started']
        )

        self.stdout.write(f'Найдено рассылок для отправки: {active_mailings.count()}')

        for mailing in active_mailings:
            self.stdout.write(f'Отправка рассылки #{mailing.id} "{mailing.message.subject}"...')

            sent, failed = send_mailing(mailing)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Рассылка #{mailing.id}: отправлено {sent}, ошибок {failed}'
                )
            )
