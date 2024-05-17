from django.db import models
from django.contrib.auth.models import User


from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)



class AdCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

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
    ad = models.ForeignKey(Ad, related_name='responses', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='responses')

    def __str__(self):
        return f'Response to {self.ad.title}'

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

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title
    
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()