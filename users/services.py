from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import CustomUser


def send_verification_email(user, request):
    """Отправляет email для подтверждения"""
    token = get_random_string(50)
    user.verification_token = token
    user.save()

    domain = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    verification_url = f"{protocol}://{domain}/users/verify/{token}/"

    subject = 'Подтверждение email адреса'
    message = f'''
    Здравствуйте, {user.username}!

    Для подтверждения вашего email адреса перейдите по ссылке:
    {verification_url}

    Если вы не регистрировались на нашем сайте, проигнорируйте это письмо.
    '''

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_email(token):
    """Подтверждает email по токену"""
    try:
        user = CustomUser.objects.get(verification_token=token)
        user.email_verified = True
        user.verification_token = None
        user.save()
        return user
    except CustomUser.DoesNotExist:
        return None
