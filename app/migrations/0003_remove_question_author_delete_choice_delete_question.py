# Generated by Django 5.0.6 on 2024-05-19 17:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_author_response_user_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='author',
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]
