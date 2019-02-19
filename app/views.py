from django.shortcuts import render, redirect
from django.http import JsonResponse
from AffichageDynamique import settings
from django.urls import reverse
from django.views.generic import ListView
from .models import Feed, Content, Subscription, Screen
from app import image_worker
from django.http import HttpResponseForbidden
from .forms import ContentFormImage
from upload_validator import FileTypeValidator

validator = FileTypeValidator(
    allowed_types=['image/jpeg', 'image/png', 'application/pdf'], allowed_extensions=['.jpg', '.jpeg', '.png', '.pdf']
)

def ContentCreateImage(request):
    form = ContentFormImage(request.POST or None)
    if form.is_valid():
        form.instance.user = request.user
        form.instance.content_type="I"
        form.instance.content_url="image"
        form.instance.state = False
        validator(request.FILES['file'])
        content = form.save()
        tmp_url = settings.BASE_DIR + '/tmp/' +  request.FILES['file'].name
        with open(tmp_url, 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        if request.FILES['file'].content_type == "application/pdf":
            image_worker.convert_pdf_to_img(tmp_url, content)
        else:
            image_worker.resize_img(tmp_url, content)
        return render(request, 'app/add_content.html', locals())
        #return redirect(reverse("home"))
    else:
        return render(request, 'app/add_content.html', locals())
    #return reverse('show_member', args=(self.object.pk,))

class Home(ListView):
    model=Feed
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Feed.objects.order_by("feed_group")
        else:
            return Feed.objects.filter(submitter_group__in=self.request.user.groups.all()).order_by("feed_group")



def content_list(request, pk):
    feed = Feed.objects.get(pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser:
        return HttpResponseForbidden()
    content = Content.objects.filter(feed=feed).order_by('-end_date')
    return render(request, 'app/content_list.html', {"content": content})



def json_screen(request, pk_screen):
    json = []
    screen = Screen.objects.get(pk=pk_screen)
    urgent = Subscription.objects.filter(subscription_type="U").filter(screen=screen)
    if urgent.count()>0:
        for subscription in urgent:
            feed = subscription.feed
            content = feed.content_feed.all()
            for img in content:
                if img.active:
                    if img.content_type=="I":
                        image1 = img.images.all()
                        for img1 in image1:
                            image = {'type': 'image', 'content': str(img1.image), 'duration': int(img.duration/image1.count())}
                            json.append(image)
    else:
        subscription1 = Subscription.objects.filter(subscription_type="N").filter(screen=screen)
        for sub in subscription1:
            feed = sub.feed
            content = feed.content_feed.all()
            for img in content:
                if img.active:
                    if img.content_type=="I":
                        image1 = img.images.all()
                        for img1 in image1:
                            image = {'type': 'image', 'content': str(img1.image), 'duration': int(img.duration/image1.count())}
                            json.append(image)
    return JsonResponse(json,safe=False)