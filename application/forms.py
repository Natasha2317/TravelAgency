from django import forms
from django.contrib.auth import get_user_model
from .models import *
from django.forms import ModelForm, TextInput, DateTimeInput, DateInput
from django.forms.widgets import ClearableFileInput, CheckboxInput
from PIL import Image
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
User = get_user_model()


class LoginForm(forms.ModelForm):
    """Форма для входа"""
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username).first()
        if not user:  # None
            raise forms.ValidationError(
                f'Пользователь с логином {username} не найден в системе')
        if not user.check_password(password):
            raise forms.ValidationError('Неверный пароль')
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    class Meta:
        model = User
        fields = ('username', 'password')



class ClientCreateForm(ModelForm):

    class Meta:
        model = Client
        fields = ['client_name', 'client_fio', 'gender', 'date_birthday', 'place_birthday', 'passport_seria', 'passport_number', 'client_status', 'passport_date_issue', 'passport_date_expiration', 'passport_authority']

        widgets = {
            "client_name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя клиента'
            }),
            "client_fio": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ФИО'
            }),
            "place_birthday": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Место рождения'
            }),
            "passport_seria": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Серия '
            }),
            "passport_number": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер'
            }),
            "passport_authority": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Орган'
            }),
        }


class WorkerCreateForm(ModelForm):

    class Meta:
        model = Worker
        fields = ['worker_name', 'worker_fio', 'date_birthday', 'photo', 'organization', 'position']


class AgentCreateForm(ModelForm):

    class Meta:
        model = Agent
        fields = ['agent_name', 'agent_fio', 'organization']


class UserCreateForm(ModelForm):
    class Meta:
        model = AuthUser
        fields = ['password', 'last_login', 'username', 'date_joined', 'is_superuser','is_staff', 'is_active']


class MyClearableFileInput(ClearableFileInput):
    initial_text = 'Текущая фотография'
    input_text = 'Изменить фотографию'
    initial_text = ugettext_lazy('Текущая фотография')
    input_text = ugettext_lazy('Изменить фотографию')
    template_with_initial = u'%(initial)s %(clear_template)s %(input_text)s: %(input)s'
    url_markup_template = '<a href="{0}">{1}</a>'
    clear_checkbox_label = 'Удалить фотографию'
    upload_to = 'static/images'

    def render(self, name, value, attrs=None, renderer=None):
        substitutions = {
            'initial_text': self.initial_text,
            'clear_template': '',
            'input_text': self.input_text,
        }
        template = '%(input)s'
        substitutions['input'] = super(MyClearableFileInput, self).render(name, value, attrs)


        return mark_safe(template % substitutions)