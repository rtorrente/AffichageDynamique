# Generated by Django 2.1.7 on 2019-03-20 13:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0009_screen_screen_control_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='date_last_moderation_email',
            field=models.DateTimeField(auto_now_add=True, null=True),
            preserve_default=False,
        ),
    ]
