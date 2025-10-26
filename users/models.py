from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона', blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар', blank=True, null=True)
    country = models.CharField(max_length=50, verbose_name='Страна', blank=True, null=True)
    email_verified = models.BooleanField(default=False, verbose_name='Email подтвержден')
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        return self.email
