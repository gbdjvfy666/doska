from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=200)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories')

    def __str__(self):
        return self.name
    


class AdCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='announcements')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('announcement-detail', args=[str(self.id)])

    def __str__(self):
        return self.title
 

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username
    
class Ad(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    category = models.ForeignKey(AdCategory, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.title

class Response(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='responses')
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('accepted', 'Accepted')), default='pending')

    def __str__(self):
        return f'Response by {self.author.username} on {self.announcement.title}'

class Question(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category_choices = [
        ('tank', 'Танки'),
        ('healer', 'Хилы'),
        ('dd', 'ДД'),
        ('trader', 'Торговцы'),
        ('guild_master', 'Гилдмастеры'),
        ('quest_giver', 'Квестгиверы'),
        ('blacksmith', 'Кузнецы'),
        ('leatherworker', 'Кожевники'),
        ('potion_maker', 'Зельевары'),
        ('spell_master', 'Мастера заклинаний'),
    ]
    category = models.CharField(max_length=20, choices=category_choices)

    def __str__(self):
        return self.title

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text    
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
    
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Response)
def send_response_notification(sender, instance, created, **kwargs):
    if created:
        announcement = instance.announcement
        recipient = announcement.author.email
        send_mail(
            'Новый отклик на ваше объявление',
            f'У вас новый отклик на объявление "{announcement.title}".',
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )