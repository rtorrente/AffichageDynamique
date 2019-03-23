import os
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from django.utils import timezone

from AffichageDynamique import settings
from .models import Image, Content, Feed, Screen

User = get_user_model()

def delete_image_orphan():
    list = os.listdir(settings.MEDIA_ROOT + "/contents")
    image = Image.objects.all()
    imagelist = []
    for img in image:
        string = img.image.name
        imagelist.append(string.replace("contents/", ""))
    for img in list:
        if img not in imagelist:
            os.remove(settings.MEDIA_ROOT + "/contents/" + img)


def delete_old_content():
    date = timezone.now() - timezone.timedelta(days=7)
    content = Content.objects.filter(end_date__lt=date)
    content.delete()
    content = Content.objects.filter(state="R").filter(begin_date__lt=date)
    content.delete()
    content = Content.objects.filter(is_valid=False).filter(submission_date__lt=date)
    content.delete()


def notify_old_user():
    date = timezone.now() - timezone.timedelta(days=365)
    user = User.objects.filter(last_login__lt=date).filter(is_active=True)
    print(user)


def notify_moderation():
    last = timezone.now() - timezone.timedelta(hours=12)
    feed_list = Feed.objects.filter(content_feed__state="P").filter(content_feed__is_valid=True).filter(
        date_last_moderation_email__lt=last).distinct()
    for feed in feed_list:
        user_list = User.objects.filter(groups=feed.moderator_group).distinct()
        for user in user_list:
            msg_plain = render_to_string('app/pending_moderation.txt',
                                         {'user': user, 'site': settings.ALLOWED_HOSTS[0], 'feed': feed})
            send_mail(
                feed.name + " - Contenu à modérer",
                msg_plain,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        feed.date_last_moderation_email = timezone.now()
        feed.save()


def notify_screen_hs():
    screen_list = Screen.objects.all()
    for screen in screen_list:
        if not screen.is_ok:
            mail_admins("Problème screen", "L'écran " + str(screen.name) + " rencontre un problème")
