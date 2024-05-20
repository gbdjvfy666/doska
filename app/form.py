from django import forms
from .models import Announcement, Response

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'category', 'image', 'video_url']

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']