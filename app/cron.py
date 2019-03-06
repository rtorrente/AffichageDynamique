import os
from django.contrib.auth import get_user_model
from django.utils import timezone

from AffichageDynamique import settings
from .models import Image, Content

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
            print(settings.MEDIA_ROOT + "/contents/" + img)
            os.remove(settings.MEDIA_ROOT + "/contents/" + img)


def delete_old_content():
    date = timezone.now() - timezone.timedelta(days=7)
    content = Content.objects.filter(end_date__lt=date)
    content.delete()


def notify_old_user():
    date = timezone.now() - timezone.timedelta(days=365)
    user = User.objects.filter(last_login__lt=date).filter(is_active=True)
    print(user)
