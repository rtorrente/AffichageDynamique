from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from AffichageDynamique import settings

User = get_user_model()

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

DAY_TYPE = [
    (1, "Lundi"),
    (2, "Mardi"),
    (3, "Mercredi"),
    (4, "Jeudi"),
    (5, "Vendredi"),
    (6, "Samedi"),
    (7, "Dimanche"),
]

SCREEN_CONTROL_TYPE = [
    (1, "None"),
    (2, "CEC RW"),
    (3, "CEC RO"),
    (4, "LG Serial"),
    (5, "RPi TV Service")
]


@receiver(post_save, sender=User)  # Ajout d'un groupe par défaut à la création d'un user si défini dans la config
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if int(settings.DEFAULT_GROUP_PK) != 0:
            group = Group.objects.get(pk=int(settings.DEFAULT_GROUP_PK))
            if group is not None:
                instance.groups.add(group)


# Début surcharge model user
def user_content_moderation_pending(self):  # Permet de savoir si l'utilisateur a du contenu à modérer
    return Feed.objects.filter(moderator_group__in=self.groups.all()).filter(content_feed__state="P").filter(
        content_feed__is_valid=True).count()


def user_is_restaurant(self):  # Permet de savoir si l'utilisateur a du contenu à modérer
    group_restaurant = Group.objects.get(pk=settings.RESTAURANTS_GROUP_PK)
    if group_restaurant in self.groups.all() or self.is_superuser:
        print("True")
        return True
    else:
        print("False")
        return False


User.add_to_class('content_moderation_pending',
                  user_content_moderation_pending)
User.add_to_class('user_is_restaurant',
                  user_is_restaurant)


# On ajoute les classes à l'User Model


# FIN surcharge model user

class HourGroup(models.Model):
    name = models.CharField(verbose_name="Nom du groupe horaire", blank=False, null=False, max_length=255)

    def __str__(self):
        return self.name


class Hour(models.Model):
    day = models.IntegerField(choices=DAY_TYPE, default='1')
    first_hour = models.TimeField()
    last_hour = models.TimeField()
    hour_group = models.ForeignKey(to=HourGroup, null=False, blank=False, related_name="hour", on_delete=models.CASCADE)

    def __str__(self):
        return self.hour_group.name + " - " + str(self.day) + " " + str(self.first_hour) + " - " + str(self.last_hour)


class Place(models.Model):
    name = models.CharField(verbose_name="Nom du groupe horaire", blank=False, null=False, max_length=255)
    hour_group = models.ForeignKey(to=HourGroup, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


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
    date_last_moderation_email = models.DateTimeField(editable=True, null=True)
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
    token = models.CharField(unique=True, max_length=32)
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
    place_group = models.ForeignKey(Place, null=True, on_delete=models.SET_NULL)
    screen_control_type = models.IntegerField(null=False, default=1, choices=SCREEN_CONTROL_TYPE)

    def __str__(self):
        return self.name

    @property
    def is_ok(self):
        time_error = timezone.now() - timezone.timedelta(minutes=10)
        # Si les appels monitoring et json sont inferieurs à 10 min et que le systeme de fichier est en RO
        if self.date_last_call > time_error and self.date_last_monitoring > time_error and self.fs_ro:
            # Si l'écran est bien allumé quand c'est censé être le cas
            if self.screen_need_on and self.tv_screen_on:
                return True
            # Si l'écran est bien éteint quand c'est censé être le cas
            elif not self.screen_need_on and not self.tv_screen_on:
                return True
            else:
                # Si exctinction auto pas activee, on considère que c'est ok quand même
                if self.screen_control_type == 1 or self.screen_control_type == 3:
                    return True
                # Sinon y'a une erreur
                else:
                    return False
        else:
            return False


    @property
    def screen_need_on(self):
        if self.place_group is not None:
            now = timezone.localtime(timezone.now())
            day = now.isoweekday()
            hour = now.time()
            hour = Hour.objects.filter(hour_group=self.place_group.hour_group).filter(day=day).filter(
                first_hour__lt=hour).filter(last_hour__gt=hour)
            if hour.count() > 0:
                return 1
            else:
                return 0
        else:  # Si aucune place group n'est définie, on laisse l'écran allumé
            return 1

    @property
    def screen_is_off(self):
        if not self.screen_need_on and not self.tv_screen_on:
            return True
        else:
            return False


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
    user_moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+", blank=True)
    reject_reason = models.TextField(null=True, default=None, blank=True)
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