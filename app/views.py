from django.shortcuts import render, redirect
from django.http import JsonResponse
from AffichageDynamique import settings
from django.urls import reverse
from django.views.generic import ListView
from .models import Feed, Content, Subscription, Screen, Image
from app import image_worker
from django.http import HttpResponseForbidden
from .forms import ContentFormImage, RejectContentForm
from upload_validator import FileTypeValidator
from django.shortcuts import get_object_or_404

validator = FileTypeValidator(
    allowed_types=['image/jpeg', 'image/png', 'application/pdf'], allowed_extensions=['.jpg', '.jpeg', '.png', '.pdf']
)


def render_specific(request, template, dict={}):
    count = Feed.objects.filter(moderator_group__in=request.user.groups.all()).filter(content_feed__state="P").count()
    dict.update({"moderate_count":count})
    return render(request, template, dict)

def ContentCreateImage(request):
    form = ContentFormImage(request.POST or None)
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
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
        if content.feed.moderator_group in request.user.groups.all() or request.user.is_superuser: #Si l'utilisateur est modérateur ou admin on modére directement
            content.state=True
        content.is_valid=True
        content.save()
        return render_specific(request, 'app/add_content.html', locals())
        #return redirect(reverse("home"))
    else:
        return render_specific(request, 'app/add_content.html', locals())
    #return reverse('show_member', args=(self.object.pk,))

def home(request):
    if request.user.is_superuser:
        feed = Feed.objects.order_by("feed_group")
    else:
        feed = Feed.objects.filter(submitter_group__in=request.user.groups.all()).order_by("feed_group")
    return render_specific(request, 'app/feed_list.html', {'feed':feed})

def content_list(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and feed.moderator_group not in request.user.groups.all():
        return HttpResponseForbidden()
    content = Content.objects.filter(feed=feed).filter(is_valid=True).order_by('-end_date')
    return render_specific(request, 'app/content_list.html', {"content": content})

def content_list_moderate(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and feed.moderator_group not in request.user.groups.all():
        return HttpResponseForbidden()
    content = Content.objects.filter(feed=feed).filter(is_valid=True).filter(state="P").order_by('begin_date')
    return render_specific(request, 'app/content_list.html', {"content": content})

def moderation_home(request):
    if request.user.is_superuser:
        feed = Feed.objects.filter(content_feed__state="P")
    else:
        feed = Feed.objects.filter(content_feed__state="P").filter(moderator_group__in=request.user.groups.all())
    return render_specific(request, 'app/moderation_home.html', {"feed": feed})

def content_view(request, pk):
    content = get_object_or_404(Content, pk=pk)
    if content.feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all():
        return HttpResponseForbidden()
    image = Image.objects.filter(content=content)
    return render_specific(request, 'app/content_view.html', {"content": content, "images":image})

def approve_content(request,pk):
    content = get_object_or_404(Content,pk=pk)
    if not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all(): #Modo ou SuperAd
        return HttpResponseForbidden()
    content.state='A'
    content.save()
    #Add approved email
    return redirect(reverse("content_list_moderate", args=[content.feed.pk]))

def reject_content(request, pk):
    form = RejectContentForm(request.POST or None)
    if form.is_valid():
        content = get_object_or_404(Content, pk=pk)
        if not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all():  # Modo ou SuperAd
            return HttpResponseForbidden()
        content.state='R'
        content.save()
        #Add reject email
        return redirect(reverse("content_list_moderate", args=[content.feed.pk]))
    else:
        return redirect(reverse("content_view", args=[pk]))

def json_screen(request, pk_screen):
    json = []
    screen = get_object_or_404(Screen,pk=pk_screen)
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
                    elif img.content_type=="Y":
                        image = {'type': 'youtube', 'content': img.content_url, 'duration': int(img.duration)}
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
                    elif img.content_type=="Y":
                        image = {'type': 'youtube', 'content': img.content_url, 'duration': int(img.duration)}
                        json.append(image)
    return JsonResponse(json,safe=False)

def display(request, pk):
    screen = get_object_or_404(Screen, pk=pk)
    return render(request, 'app/display.html', {"pk": screen.pk})