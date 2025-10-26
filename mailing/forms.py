from django import forms
from .models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['message', 'clients']
        widgets = {
            'message': forms.Select(attrs={'class': 'form-control'}),
            'clients': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '10'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        if user:
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['clients'].queryset = Client.objects.filter(owner=user)
