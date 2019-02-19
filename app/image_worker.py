from PyPDF2 import PdfFileReader
from wand.image import Image
from django.utils import six
import os
from .models import Image as ImageModel

def convert_pdf_to_img(file1, content):
    size = '_' + str(1920) + 'x' + str(1080) + 'px'
    input_file = PdfFileReader(open(file1, 'rb'))
    for i in range(input_file.getNumPages()):
        with Image(filename = file1 + '[' + str(i) + ']') as img:
            if len(size) > 0:
                img.resize(1920, 1080)
            img.format = "png"
            stream_out = six.BytesIO()
            img.save(file=stream_out)
            picture = ImageModel()
            picture.content = content
            picture.image.save(name="FileUpload.png", content=stream_out)
            picture.save()
    os.remove(file1)

def resize_img(file1, content):
    img = Image(filename=file1)
    if(img.width>1920):
        img.sample(width=1920)
    if(img.height>1080):
        img.sample(height=1080)
    img.format = "png"
    stream_out = six.BytesIO()
    img.save(file=stream_out)
    picture = ImageModel()
    picture.content = content
    picture.image.save(name="FileUpload.png", content=stream_out)
    picture.save()
    os.remove(file1)