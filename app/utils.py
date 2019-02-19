from AffichageDynamique import settings
import os
from .models import Image, Content
from django.utils import timezone


def delete_image_orphan():
    list = os.listdir(settings.MEDIA_ROOT + "/contents")
    image = Image.objects.all()
    imagelist=[]
    for img in image:
        string = img.image.name
        imagelist.append(string.replace("contents/", ""))
    for img in list:
        if img not in imagelist:
            print (settings.MEDIA_ROOT + "/contents/"+img)
            os.remove(settings.MEDIA_ROOT + "/contents/"+img)

def delete_old_content(days):
    date = timezone.now() - timezone.timedelta(days=days)
    content = Content.objects.filter(end_date__lt=date)
    content.delete()
