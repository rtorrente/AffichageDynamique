# Generated by Django 2.1.7 on 2019-03-27 01:50

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0015_auto_20190327_0204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen',
            name='date_last_problem_email',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]