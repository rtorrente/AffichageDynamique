from django.shortcuts import render, redirect
from AffichageDynamique import settings
from django.urls import reverse
from django.views.generic import ListView
from .models import Feed, Content
from app import image_worker
from django.http import HttpResponseForbidden
from .forms import ContentFormImage

def ContentCreateImage(request):
    form = ContentFormImage(request.POST or None)
    if form.is_valid():
        form.instance.user = request.user
        form.instance.content_type="I"
        form.instance.content_url="image"
        form.instance.state = False
        print (request.FILES['file'].content_type)
        with open(settings.MEDIA_ROOT + '/upload/' +  request.FILES['file'].name, 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        if request.FILES['file'].content_type == "application/pdf":
            print ('pdf')
            image_worker.convert_pdf_to_img(settings.MEDIA_ROOT + '/upload/' +  request.FILES['file'].name, None)
        return render(request, 'app/add_content.html', locals())
        #form.save()
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