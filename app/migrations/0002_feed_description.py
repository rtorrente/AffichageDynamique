# Generated by Django 2.1.7 on 2019-02-20 13:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Description du flux'),
        ),
    ]
