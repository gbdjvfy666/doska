from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f'Response to {self.ad.title}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title
    
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class Category(models.Model):
    pass