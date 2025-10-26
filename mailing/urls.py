from django.urls import path
from . import views
from .apps import MailingConfig
from .views import MessageDetailView

app_name = MailingConfig.name

urlpatterns = [

    path('', views.index, name='index'),

    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', views.MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),

    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_edit'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.MailingSendView.as_view(), name='mailing_send'),

    path('manager/users/', views.UserListView.as_view(), name='user_list'),
    path('manager/users/<int:pk>/block/', views.UserBlockView.as_view(), name='user_block'),
    path('manager/mailings/<int:pk>/disable/', views.MailingDisableView.as_view(), name='mailing_disable')

]