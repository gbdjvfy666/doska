from django import forms
from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'category', 'image', 'video_url']


from django import forms
from .models import Ad, Response

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title']

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']