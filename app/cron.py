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


def delete_old_user():
    date = timezone.now() - timezone.timedelta(days=365)
    user_list = User.objects.filter(last_login__lt=date).filter(is_active=True).filter(is_superuser=False)
    for user in user_list:
        date_supression = (user.last_login + timezone.timedelta(days=395)).date()
        if timezone.now().date() <= date_supression:
            msg_plain = render_to_string('app/email_inactive.txt',
                                         {'user': user, 'date_supression': date_supression,
                                          "site": settings.ALLOWED_HOSTS[0]})
            send_mail(
                settings.EMAIL_SUBJECT_PREFIX + " Compte inactif",
                msg_plain,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        else:
            user.delete()


def notify_moderation():
    last = timezone.now() - timezone.timedelta(hours=12)
    feed_list = Feed.objects.filter(content_feed__state="P", content_feed__is_valid=True).filter(
        date_last_moderation_email__lt=last).distinct()
    for feed in feed_list:
        user_list = User.objects.filter(groups=feed.moderator_group).distinct()
        for user in user_list:
            msg_plain = render_to_string('app/email_pending_moderation.txt',
                                         {'user': user, 'site': settings.ALLOWED_HOSTS[0], 'feed': feed})
            send_mail(
                settings.EMAIL_SUBJECT_PREFIX + " " + feed.name + " - Contenu à modérer",
                msg_plain,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        feed.date_last_moderation_email = timezone.now()
        feed.save()


def notify_screen_hs():
    last = timezone.now() - timezone.timedelta(hours=6)
    screen_list = Screen.objects.all()
    for screen in screen_list:
        if not screen.is_ok and screen.date_last_problem_email < last:
            msg_plain = render_to_string('app/email_screen_hs.txt',
                                         {'screen': screen})
            mail_admins("Problème écran " + screen.name, msg_plain)
            screen.date_last_monitoring = timezone.now()
            screen.save()
        # Magouille pour permettre de resignaler si le screen devient ok et rebug
        elif screen.is_ok and screen.date_last_problem_email > last:
            last_fake = timezone.now() - timezone.timedelta(days=1)
            screen.date_last_monitoring = last_fake
            screen.save()
