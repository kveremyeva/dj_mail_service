from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from mailing.forms import ClientForm, MessageForm, MailingForm
from mailing.models import Client, Mailing, Message, MailingAttempt
from mailing.services import send_mailing
from users.models import CustomUser


class OwnerMixin(UserPassesTestMixin):
    """Универсальный миксин для проверки владельца объекта"""
    def test_func(self):
        if hasattr(self, 'get_object'):
            obj = self.get_object()
        else:
            obj = get_object_or_404(self.model, pk=self.kwargs['pk'])
        return obj.owner == self.request.user


class OwnerListMixin:
    """Миксин для ListView - фильтрует только объекты владельца"""
    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)


class ManagerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки роли менеджера"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_manager()


class ManagerAccessMixin:
    """Миксин для предоставления доступа менеджеру ко всем объектам"""
    def get_queryset(self):
        if self.request.user.is_manager():
            return self.model.objects.all()
        return self.model.objects.filter(owner=self.request.user)


@cache_page(60 * 5)
def index(request):
    """Главная страница со статистикой"""
    if request.user.is_authenticated:
        total_mailings = Mailing.objects.filter(owner=request.user).count()
        active_mailings = Mailing.objects.filter(
            owner=request.user,
            status='started'
        ).count()
        unique_clients = Client.objects.filter(owner=request.user).count()
    else:
        total_mailings = active_mailings = unique_clients = 0

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
    }
    return render(request, 'mailing/index.html', context)


class ClientListView(LoginRequiredMixin, OwnerListMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(OwnerMixin, LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')


class ClientDeleteView(OwnerMixin, LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')


class MessageListView(LoginRequiredMixin, OwnerListMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'


class MessageDetailView(OwnerMixin, LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(OwnerMixin, LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(OwnerMixin, LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')


class MailingListView(LoginRequiredMixin, OwnerListMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(OwnerMixin, LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingDeleteView(OwnerMixin, LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDetailView(OwnerMixin, LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = MailingAttempt.objects.filter(
            mailing=self.object
        ).order_by('-attempt_time')
        return context


class MailingSendView(OwnerMixin, LoginRequiredMixin, View):
    """Ручная отправка рассылки"""
    model = Mailing

    def post(self,request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.status == 'completed':
            print(f"Рассылка #{mailing.id} уже завершена")
        else:
            sent, failed = send_mailing(mailing)
            print(f"Рассылка #{mailing.id} отправлена. Успешно: {sent}, Ошибок: {failed}")

        return redirect('mailing:mailing_detail', pk=pk)


class UserListView(ManagerRequiredMixin, ListView):
    """Просмотр списка пользователей (только для менеджеров)"""
    model = CustomUser
    template_name = 'mailing/user_list.html'
    context_object_name = 'users'


class UserBlockView(ManagerRequiredMixin, View):
    """Блокировка/разблокировка пользователя"""
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if user != request.user:  # Нельзя заблокировать себя
            user.is_active = not user.is_active
            user.save()
        return redirect('mailing:user_list')


class MailingDisableView(ManagerRequiredMixin, View):
    """Отключение рассылки менеджером"""
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = 'completed'
        mailing.save()
        return redirect('mailing:mailing_list')