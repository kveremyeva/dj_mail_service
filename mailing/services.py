from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import MailingAttempt


def send_mailing(mailing):
    """Отправляет рассылку всем клиентам и создает записи о попытках"""
    if not mailing.start_time:
        mailing.start_time = timezone.now()
        mailing.status = 'started'
        mailing.save()

    clients = mailing.clients.all()
    total_sent = 0
    total_failed = 0

    for client in clients:
        try:
            result = send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )

            if result == 1:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='Письмо успешно отправлено',
                    owner=mailing.owner
                )
                total_sent += 1
            else:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='failure',
                    server_response='Ошибка отправки'
                )
                total_failed += 1

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failure',
                server_response=f'Ошибка: {str(e)}',
                owner=mailing.owner
            )
            total_failed += 1

    mailing.end_time = timezone.now()
    mailing.status = 'completed'
    mailing.save()

    return total_sent, total_failed
