# Generated by Django 2.1.7 on 2019-02-20 13:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0002_feed_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
