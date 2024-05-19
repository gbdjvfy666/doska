from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Response

@receiver(post_save, sender=Response)
def send_response_notification(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Новый отклик на ваше объявление',
            f'Ваше объявление "{instance.announcement.title}" получило новый отклик.',
            'from@example.com',
            [instance.announcement.author.email],
            fail_silently=False,
        )

@receiver(post_save, sender=Response)
def send_accept_notification(sender, instance, **kwargs):
    if instance.status == 'accepted':
        send_mail(
            'Ваш отклик принят',
            f'Ваш отклик на объявление "{instance.announcement.title}" был принят.',
            'from@example.com',
            [instance.user.email],
            fail_silently=False,
        )