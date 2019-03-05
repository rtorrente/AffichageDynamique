from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.forms import HiddenInput
from django.http import HttpResponseForbidden, HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView
from upload_validator import FileTypeValidator

from AffichageDynamique import settings
from app import image_worker
from .forms import ContentFormImage, RejectContentForm, ScreenMonitoringEndpoint, SubscriptionForm, ContentFormYoutube, \
    ContentFormUrl
from .models import Feed, Content, Subscription, Screen, Image

User = get_user_model()

validator = FileTypeValidator(
    allowed_types=['image/jpeg', 'image/png', 'application/pdf'], allowed_extensions=['.jpg', '.jpeg', '.png', '.pdf']
)


class UserUpdate(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'registration/user_update.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user

def ContentCreateImage(request):
    form = ContentFormImage(request.POST or None)
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
    if form.is_valid():
        form.instance.user = request.user
        form.instance.content_type="I"
        form.instance.content_url="image"
        form.instance.state = 'P'
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
            content.state="A"
        content.is_valid=True
        content.save()
        return redirect(reverse("content_list", args=[content.feed.pk]))
    else:
        return render(request, 'app/add_content.html', locals())

def ContentCreateYoutube(request):
    form = ContentFormYoutube(request.POST or None)
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
    if form.is_valid():
        form.instance.user = request.user
        form.instance.content_type = "Y"
        form.instance.state = 'P'
        content = form.save()
        if content.feed.moderator_group in request.user.groups.all() or request.user.is_superuser:  # Si l'utilisateur est modérateur ou admin on modére directement
            content.state = "A"
        content.is_valid = True
        content.save()
        return redirect(reverse("content_list", args=[content.feed.pk]))
    else:
        return render(request, 'app/add_content.html', locals())


def ContentCreateUrl(request):
    form = ContentFormUrl(request.POST or None)
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
    if form.is_valid():
        form.instance.user = request.user
        form.instance.content_type = "U"
        form.instance.state = 'P'
        content = form.save()
        if content.feed.moderator_group in request.user.groups.all() or request.user.is_superuser:  # Si l'utilisateur est modérateur ou admin on modére directement
            content.state = "A"
        content.is_valid = True
        content.save()
        return redirect(reverse("content_list", args=[content.feed.pk]))
    else:
        return render(request, 'app/add_content.html', locals())

def home(request):
    if request.user.is_superuser:
        feed = Feed.objects.order_by("feed_group")
    else:
        feed = Feed.objects.filter(submitter_group__in=request.user.groups.all()).order_by("feed_group")
    return render(request, 'app/feed_list.html', {'feed': feed})

def content_list(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and feed.moderator_group not in request.user.groups.all():
        return HttpResponseForbidden()
    content = Content.objects.filter(feed=feed).filter(is_valid=True).order_by('-end_date')
    return render(request, 'app/content_list.html', {"content": content})

def content_list_moderate(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and feed.moderator_group not in request.user.groups.all():
        return HttpResponseForbidden()
    content = Content.objects.filter(feed=feed).filter(is_valid=True).filter(state="P").order_by('begin_date')
    return render(request, 'app/content_list.html', {"content": content})

def moderation_home(request):
    if request.user.is_superuser:
        feed = Feed.objects.filter(content_feed__state="P").distinct()
    else:
        feed = Feed.objects.filter(content_feed__state="P").filter(
            moderator_group__in=request.user.groups.all()).distinct()
    return render(request, 'app/moderation_home.html', {"feed": feed})

def content_view(request, pk):
    content = get_object_or_404(Content, pk=pk)
    form = RejectContentForm(None)
    if content.feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all():
        return HttpResponseForbidden()
    image = Image.objects.filter(content=content)
    return render(request, 'app/content_view.html', {"content": content, "images": image, "form": form})

def approve_content(request,pk):
    content = get_object_or_404(Content,pk=pk)
    if not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all(): #Modo ou SuperAd
        return HttpResponseForbidden()
    content.state='A'
    content.save()
    msg_plain = render_to_string('app/email_approved.txt', {'user': content.user, 'content': content})
    send_mail(
        'Validation de votre affichage',
        msg_plain,
        settings.DEFAULT_FROM_EMAIL,
        [content.user.email],
    )
    return redirect(reverse("content_list_moderate", args=[content.feed.pk]))

def reject_content(request, pk):
    form = RejectContentForm(request.POST or None)
    if form.is_valid():
        content = get_object_or_404(Content, pk=pk)
        if not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all():  # Modo ou SuperAd
            return HttpResponseForbidden()
        content.state='R'
        content.save()
        message = form.cleaned_data['reason']
        msg_plain = render_to_string('app/email_rejected.txt',
                                     {'user': content.user, 'content': content, 'message': message})
        send_mail(
            'Refus de votre affichage',
            msg_plain,
            settings.DEFAULT_FROM_EMAIL,
            [content.user.email],
        )
        return redirect(reverse("content_list_moderate", args=[content.feed.pk]))
    else:
        return redirect(reverse("content_view", args=[pk]))

def json_screen(request, token_screen):
    json = []
    screen = get_object_or_404(Screen,token=token_screen)
    screen.date_last_call = timezone.now()  # On enregistre l'appel au json (pour le monitoring)
    screen.save()
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
                    elif img.content_type=="U":
                        image = {'type': 'iframe', 'content': img.content_url, 'duration': int(img.duration)}
                        json.append(image)
    return JsonResponse(json,safe=False)

def display(request, token_screen):
    try:
        screen = Screen.objects.get(token=token_screen)
        if settings.DEBUG:
            debug = 1
        else:
            debug = 0
        return render(request, 'app/display.html',
                  {"screen": screen, "media": settings.MEDIA_URL, "static": settings.STATIC_URL,
                   "debug": debug})
    except:
        return render(request, 'app/display_new_screen.html', {"token": token_screen})



def list_screen(request):
    if request.user.is_superuser:
        screen = Screen.objects.all()
    else:
        screen = Screen.objects.filter(hidden=False)
    return render(request, 'app/list_screen.html', {"screen": screen})


def view_screen(request, pk_screen):
    screen = get_object_or_404(Screen, pk=pk_screen)
    if not request.user.is_superuser and screen.hidden and screen.owner_group not in request.user.groups.all():
        return HttpResponseForbidden()
    urgent = Subscription.objects.filter(screen=screen).filter(subscription_type="U").order_by("-priority")
    normal = Subscription.objects.filter(screen=screen).filter(subscription_type="N").order_by("-priority")
    return render(request, 'app/view_screen.html',
                  {"screen": screen, "urgent": urgent, "normal": normal})


def delete_subscription(request, pk_sub):
    subscription = get_object_or_404(Subscription, pk=pk_sub)
    if not request.user.is_superuser and subscription.screen.owner_group not in request.user.groups.all():
        return HttpResponseForbidden()
    subscription.delete()
    return redirect(reverse("view_screen", args=[subscription.screen.pk]))


def up_subscription(request, pk_sub):
    subscription = get_object_or_404(Subscription, pk=pk_sub)
    if not request.user.is_superuser and subscription.screen.owner_group not in request.user.groups.all():
        return HttpResponseForbidden()
    if subscription.priority < 10:
        subscription.priority += 1
        subscription.save()
    return redirect(reverse("view_screen", args=[subscription.screen.pk]))


def down_subscription(request, pk_sub):
    subscription = get_object_or_404(Subscription, pk=pk_sub)
    if not request.user.is_superuser and subscription.screen.owner_group not in request.user.groups.all():
        return HttpResponseForbidden()
    if subscription.priority > 1:
        subscription.priority -= 1
        subscription.save()
    return redirect(reverse("view_screen", args=[subscription.screen.pk]))

def add_subscription(request, pk_screen, type_sub):
    screen = get_object_or_404(Screen, pk=pk_screen)
    if not request.user.is_superuser and screen.owner_group not in request.user.groups.all():
        return HttpResponseForbidden()
    form = SubscriptionForm(request.POST or None)
    if type_sub == "U":
        form.fields["priority"].initial = 1
        form.fields["priority"].widget = HiddenInput()
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
    if form.is_valid():
        if not type_sub == "N" and not type_sub == "U":
            return HttpResponseForbidden()
        form.instance.subscription_type = type_sub
        form.instance.screen = screen
        form.save()
        return redirect(reverse("view_screen", args=[screen.pk]))
    return render(request, 'app/add_subscription.html', {"form": form, "screen": screen, "type_sub": type_sub})


@csrf_exempt
def screen_monitoring_endpoint(request):
    try:
        form = ScreenMonitoringEndpoint(request.POST or None)
        if form.is_valid():
            screen = Screen.objects.get(token=form.cleaned_data['token'])
            screen.temperature = form.cleaned_data['temperature']
            screen.load = form.cleaned_data['load']
            screen.fs_ro = form.cleaned_data['fs_ro']
            screen.tv_screen_on = form.cleaned_data['tv_screen_on']
            screen.hostname = form.cleaned_data['hostname']
            screen.ip = form.cleaned_data['ip']
            screen.date_last_monitoring = timezone.now()
            screen.save()
            return HttpResponse(screen.screen_need_on)
        return HttpResponse(3)
    except:
        return HttpResponse(3)  # Si l'écran n'est pas encore enregistré
