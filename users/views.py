from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .services import verify_email


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:register_success')

    def form_valid(self, form):
        user = form.save()

        from .services import send_verification_email
        send_verification_email(user, self.request)

        self.send_welcome_email(user.email)

        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать в наш сервис'
        message = 'Спасибо за регистрацию! Проверьте вашу почту для подтверждения email.'
        from_email = 'kveremyeva@yandex.ru'
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)


class RegisterSuccessView(TemplateView):
    """Страница успешной регистрации"""
    template_name = 'users/register_success.html'


class VerifyEmailView(View):
    """Подтверждение email"""

    def get(self, request, token):
        user = verify_email(token)
        if user:
            from django.contrib.auth import login
            login(request, user)
            return render(request, 'users/verification_success.html')
        else:
            return render(request, 'users/verification_error.html')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        return reverse_lazy('mailing:index')


class CustomLogoutView(LogoutView):
    template_name = 'users/logout.html'
    next_page = reverse_lazy('mailing:index')
