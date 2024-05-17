from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category')

from django.contrib import admin
from .models import Category, AdCategory

admin.site.register(Category)
admin.site.register(AdCategory)

