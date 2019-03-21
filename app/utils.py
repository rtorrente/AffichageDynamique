import os
from PyPDF2 import PdfFileReader
from django.shortcuts import render
from django.utils import six
from wand.color import Color
from wand.image import Image

from AffichageDynamique import settings
from .models import Image as ImageModel


def convert_pdf_to_img(file1, content):
    size = '_' + str(1920) + 'x' + str(1080) + 'px'
    input_file = PdfFileReader(open(file1, 'rb'))
    for i in range(input_file.getNumPages()):
        with Image(filename=file1 + '[' + str(i) + ']', resolution=300) as img:
            if img.height != 1080:
                img.resize(height=1080)
            if img.width > 1920:
                img.resize(width=1920)
            img.format = "png"
            img.background_color = Color('white')
            img.alpha_channel = 'remove'
            stream_out = six.BytesIO()
            img.save(file=stream_out)
            picture = ImageModel()
            picture.content = content
            picture.image.save(name="content" + str(content.pk) + ".png", content=stream_out)
            picture.save()
    os.remove(file1)


def resize_img(file1, content):
    img = Image(filename=file1)
    if(img.width>1920):
        img.resize(width=1920)
    if(img.height>1080):
        img.resize(height=1080)
    img.format = "png"
    stream_out = six.BytesIO()
    img.alpha_channel = 'remove'
    img.save(file=stream_out)
    picture = ImageModel()
    picture.content = content
    picture.image.save(name="content" + str(content.pk) + ".png", content=stream_out)
    picture.save()
    os.remove(file1)


def save_image(file, content, user):
    tmp_url = settings.BASE_DIR + '/tmp/' + file.name
    with open(tmp_url, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    if file.content_type == "application/pdf":
        convert_pdf_to_img(tmp_url, content)
    else:
        resize_img(tmp_url, content)
    # Si l'utilisateur est modérateur ou admin on modére directement
    if content.feed.moderator_group in user.groups.all() or user.is_superuser:
        content.state = "A"
    content.is_valid = True
    content.save()


def denied(request):
    return render(request, "denied.html")


def json_append(subscription_list):
    json = []
    for subscription in subscription_list:
        content = subscription.feed.content_feed.all()
        for img in content:
            if img.active:
                if img.content_type == "I":
                    image1 = img.images.all()
                    for img1 in image1:
                        image = {'type': 'image', 'content': str(img1.image),
                                 'duration': int(img.duration / image1.count())}
                        json.append(image)
                elif img.content_type == "Y":
                    image = {'type': 'youtube', 'content': img.content_url, 'duration': int(img.duration)}
                    json.append(image)
                elif img.content_type == "U":
                    image = {'type': 'iframe', 'content': img.content_url, 'duration': int(img.duration)}
                    json.append(image)
                elif img.content_type == "Y":
                    image = {'type': 'youtube', 'content': img.content_url, 'duration': int(img.duration)}
                    json.append(image)
    return json
