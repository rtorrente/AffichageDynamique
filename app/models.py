from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
CONTENT_TYPE = [
    ('I', "Image"),
    ('U', "URL")
]

SUBSCRIPTION_TYPE = [
    ('N', "Normal"),
    ('U', "Urgent")
]

# Create your models here.


class Content(models.Model):
    name = models.CharField(verbose_name='Nom du contenu', blank=False, max_length=255, null=False)
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    begin_date = models.DateTimeField(blank=False, null=False)
    end_date = models.DateTimeField(blank = False, null=False)
    submission_date = models.DateTimeField(auto_now_add=True)
    content_type = models.CharField(max_length=1, choices=CONTENT_TYPE, default='I')
    content_url = models.CharField(verbose_name='Url du contenu', blank=False, max_length=255, null=True)
    content_file = models.ImageField(upload_to='contents')
    state = models.BooleanField(null=False, default=False)
    def __str__(self):
        return self.name

class FeedGroup(models.Model):
    name = models.CharField(verbose_name='Nom du groupe de flux', blank=False, max_length=255, null=False)
    owner_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1)
    def __str__(self):
        return self.name

class Feed(models.Model):
    name = models.CharField(verbose_name='Nom du flux', blank=False, max_length=255, null=False)
    owner_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1)
    feed_group = models.ForeignKey(FeedGroup, on_delete=models.PROTECT, null=True, blank=True)
    def __str__(self):
        return self.name

class Screen(models.Model):
    name = models.CharField(verbose_name="Nom de l'écran", blank=False, max_length=255, null=False)
    place = models.CharField(verbose_name="Lieu de l'écran", blank=False, max_length=255, null=False)
    owner_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1)
    def __str__(self):
        return self.name

class Subscription(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, null=True, blank=True)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=True, blank=True)
    subscription_type = models.CharField(max_length=1, choices=SUBSCRIPTION_TYPE, default='N')
    priority = models.IntegerField(verbose_name="Priorité")
    def __str__(self):
        return self.feed.name + ' - ' + self.screen.name