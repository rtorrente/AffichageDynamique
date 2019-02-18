from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils import timezone
from AffichageDynamique import settings
CONTENT_TYPE = [
    ('I', "Image uploadée"),
    ('U', "URL")
]

SUBSCRIPTION_TYPE = [
    ('N', "Normal"),
    ('U', "Urgent")
]

# Create your models here.

class FeedGroup(models.Model):
    name = models.CharField(verbose_name='Nom du groupe de flux', blank=False, max_length=255, null=False)
    owner_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1)
    def __str__(self):
        return self.name
    def count_feed(self, group):
        return int(Feed.objects.filter(owner_group=group).filter(feed_group=self).count())

class Feed(models.Model):
    name = models.CharField(verbose_name='Nom du flux', blank=False, max_length=255, null=False)
    submitter_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1)
    feed_group = models.ForeignKey(FeedGroup, on_delete=models.PROTECT, null=True, blank=True)
    def __str__(self):
        return self.feed_group.name + " - " + self.name
    @property
    def count_active(self):
        content = Content.objects.filter(feed=self)
        sum = 0
        for cont in content:
            if cont.active:
                sum = sum + 1
        return sum


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

class Content(models.Model):
    name = models.CharField(verbose_name='Nom du contenu', blank=False, max_length=255, null=False)
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    begin_date = models.DateTimeField(blank=False, null=False)
    end_date = models.DateTimeField(blank = False, null=False)
    submission_date = models.DateTimeField(auto_now_add=True)
    content_type = models.CharField(max_length=1, choices=CONTENT_TYPE, default='I')
    content_url = models.CharField(verbose_name='Url du contenu', blank=False, max_length=255, null=True)
    state = models.BooleanField(null=False, default=False)
    feed = models.ManyToManyField(Feed, related_name="content_feed", blank=False)
    duration = models.IntegerField(verbose_name="Durée")
    def __str__(self):
        return self.name
    @property
    def future(self):
        d = timezone.now()
        return d < self.begin_date
    @property
    def past(self):
        d = timezone.now()
        return d > self.end_date
    @property
    def active(self):
        if self.state == 1 and not self.future and not self.past:
            return True
        else:
            return False
    @property
    def get_first_content_url(self):
        return settings.MEDIA_URL + str(self.images.first().image)

class Image(models.Model):
    image = models.ImageField(upload_to='contents')
    content = models.ForeignKey(Content, related_name="images", on_delete=models.CASCADE)
    def __str__(self):
        return self.content.name + " - Image id " + str(self.pk)