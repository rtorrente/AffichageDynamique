import uuid
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from AffichageDynamique import settings

CONTENT_TYPE = [
    ('I', "Image uploadée"),
    ('U', "URL"),
    ('Y', "Youtube")
]

CONTENT_STATUT = [
    ('P', "En attente"),
    ('A', "Approuvé"),
    ('R', "Rejeté")
]

SUBSCRIPTION_TYPE = [
    ('N', "Normal"),
    ('U', "Urgent")
]

# Create your models here.


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if int(settings.DEFAULT_GROUP_PK) != 0:
            group = Group.objects.get(pk=int(settings.DEFAULT_GROUP_PK))
            if group is not None:
                instance.groups.add(group)


class FeedGroup(models.Model):
    name = models.CharField(verbose_name='Nom du groupe de flux', blank=False, max_length=255, null=False)
    def __str__(self):
        return self.name
    def count_feed(self, group):
        return int(Feed.objects.filter(owner_group=group).filter(feed_group=self).count())

class Feed(models.Model):
    name = models.CharField(verbose_name='Nom du flux', blank=False, max_length=255, null=False)
    description = models.CharField(verbose_name='Description du flux', blank=True, max_length=255, null=True)
    submitter_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1, related_name="feed_submitter")
    moderator_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1, related_name="feed_moderator")
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
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Nom de l'écran", blank=False, max_length=255, null=False)
    place = models.CharField(verbose_name="Lieu de l'écran", blank=False, max_length=255, null=False)
    owner_group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default=1)
    date_last_call = models.DateTimeField()
    date_last_monitoring = models.DateTimeField(null=True)
    temperature = models.FloatField(blank=True, null=True)
    load = models.CharField(max_length=16, blank=True, null=True)
    fs_ro = models.BooleanField(default=False)
    tv_screen_on = models.BooleanField(default=False)
    hostname=models.CharField(blank=True, null=True, max_length=50)
    ip = models.GenericIPAddressField(blank=True, null=True)
    hidden = models.BooleanField(default=False)
    def __str__(self):
        return self.name

    @property
    def is_ok(self):
        return True

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
    begin_date = models.DateTimeField(verbose_name="Début d'affichage", blank=False, null=False)
    end_date = models.DateTimeField(verbose_name="Fin d'affichage", blank = False, null=False)
    submission_date = models.DateTimeField(auto_now_add=True)
    content_type = models.CharField(max_length=1, choices=CONTENT_TYPE, default='I')
    content_url = models.CharField(verbose_name='Url du contenu', blank=False, max_length=255, null=True)
    state = models.CharField(max_length=1, choices=CONTENT_STATUT, default='P')
    is_valid = models.BooleanField(null=False, default=False)
    feed = models.ForeignKey(Feed, verbose_name="Flux d'affichage", related_name="content_feed", blank=False, null=False, on_delete=models.CASCADE)
    duration = models.IntegerField(verbose_name="Durée d'apparition à l'écran")
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
        if self.state == 'A' and not self.future and not self.past:
            return True
        else:
            return False
    @property
    def get_first_content_url(self):
        if self.content_type == "I":
            image = self.images.first()
            if image is not None:
                return image.get_image_url
            else:
                return "error"
        elif self.content_type == "Y":
            return settings.STATIC_URL + "youtube.png"
        elif self.content_type == "U":
            return settings.STATIC_URL + "url.png"

class Image(models.Model):
    image = models.ImageField(upload_to='contents')
    content = models.ForeignKey(Content, related_name="images", on_delete=models.CASCADE)
    def __str__(self):
        return self.content.name + " - Image id " + str(self.pk)
    @property
    def get_image_url(self):
        return settings.MEDIA_URL + str(self.image)