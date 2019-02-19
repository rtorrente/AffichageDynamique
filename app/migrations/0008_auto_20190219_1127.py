# Generated by Django 2.1.7 on 2019-02-19 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('app', '0007_auto_20190219_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='moderator_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='feed_moderator', to='auth.Group'),
        ),
        migrations.RemoveField(
            model_name='content',
            name='feed',
        ),
        migrations.AddField(
            model_name='content',
            name='feed',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='content_feed', to='app.Feed'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feed',
            name='submitter_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='feed_submitter', to='auth.Group'),
        ),
    ]
