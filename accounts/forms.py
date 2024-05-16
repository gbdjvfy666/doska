from allauth.account.forms import SignupForm

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives, mail_managers, mail_admins


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")
    password1 = forms.CharField(label="Пароль")
    password2 = forms.CharField(label="Повторите пароль")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)

        mail_managers(
            subject='Новый пользователь!',
            message=f'Пользователь {user.username} зарегистрировался на сайте.'
        )

        mail_admins(
            subject='Новый пользователь!',
            message=f'Пользователь {user.username} зарегистрировался на сайте.'
        )

        subject = 'Добро пожаловать в "Доску объявлений"!'
        text = f'{user.username}, Вы успешно зарегистрировались на сайте!'
        html = (
            f'<b>{user.username}</b>, Вы успешно зарегистрировались на '
            f'<a href="http://127.0.0.1:8000/app">сайте</a>!'
        )
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[user.email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        return user
