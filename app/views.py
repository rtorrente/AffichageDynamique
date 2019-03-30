from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail import send_mail, mail_admins
from django.forms import HiddenInput
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView
from upload_validator import FileTypeValidator

from AffichageDynamique import settings
from app import utils
from .forms import ContentFormImage, RejectContentForm, ScreenMonitoringEndpoint, SubscriptionForm, ContentFormYoutube, \
    ContentFormUrl, RestaurantForm
from .models import Feed, Content, Subscription, Screen, Image, Hour

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


def content_create_image(request):
    form = ContentFormImage(request.POST or None)
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
    if form.is_valid():
        form.instance.user = request.user
        form.instance.content_type = "I"
        form.instance.content_url = "image"
        form.instance.state = 'P'
        validator(request.FILES['file'])
        content = form.save()
        utils.save_image(request.FILES['file'], content, request.user)
        return redirect(reverse("content_list", args=[content.feed.pk]))
    else:
        return render(request, 'app/add_content.html', locals())


def content_create_youtube(request):
    form = ContentFormYoutube(request.POST or None)
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
    if form.is_valid():
        form.instance.user = request.user
        form.instance.content_type = "Y"
        form.instance.state = 'P'
        content = form.save()
        # Si l'utilisateur est modérateur ou admin on modére directement
        if content.feed.moderator_group in request.user.groups.all() or request.user.is_superuser:
            content.state = "A"
        content.is_valid = True
        content.save()
        return redirect(reverse("content_list", args=[content.feed.pk]))
    else:
        return render(request, 'app/add_content.html', {"form": form})


def content_create_url(request):
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
        return render(request, 'app/add_content.html', {"form": form})


def home(request):
    stat = {}
    if request.user.is_superuser:
        feed_home = Feed.objects.order_by("feed_group")
        stat['since_creation'] = Content.objects.latest("pk").pk
        feed_list = Feed.objects.all()
        stat['active'] = 0
        for feed in feed_list:
            stat['active'] += feed.count_active
        screen_list = Screen.objects.all()
        stat['screen_total'] = screen_list.count()
        stat['screen_ok'] = 0
        stat['screen_on'] = 0
        time_error = timezone.now() - timezone.timedelta(minutes=10)
        for screen in screen_list:
            if screen.is_ok:
                stat['screen_ok'] += 1
            if not screen.tv_screen_on and screen.date_last_call > time_error:
                stat['screen_on'] += 1
        stat['user_total'] = User.objects.latest("pk").pk
        stat['user_active'] = User.objects.filter(is_active=True).count()
    else:
        feed_home = Feed.objects.filter(submitter_group__in=request.user.groups.all()).order_by("feed_group")
    return render(request, 'app/home.html', {'feed': feed_home, 'stat': stat})


def content_list(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and feed.moderator_group not in request.user.groups.all():
        return utils.denied(request)
    content = Content.objects.filter(feed=feed).filter(is_valid=True).order_by('-end_date')
    return render(request, 'app/content_list.html', {"content": content})


def content_list_moderate(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and feed.moderator_group not in request.user.groups.all():
        return utils.denied(request)
    content = Content.objects.filter(feed=feed).filter(is_valid=True).filter(state="P").order_by('begin_date')
    return render(request, 'app/content_list.html', {"content": content})


def moderation_home(request):
    if request.user.is_superuser:
        feed = Feed.objects.filter(content_feed__state="P", content_feed__is_valid=True).distinct()
    else:
        feed = Feed.objects.filter(content_feed__state="P", content_feed__is_valid=True).filter(
            moderator_group__in=request.user.groups.all()).distinct()
    return render(request, 'app/moderation_home.html', {"feed": feed})


def content_view(request, pk):
    content = get_object_or_404(Content, pk=pk)
    form = RejectContentForm(None)
    if content.feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all():
        return utils.denied(request)
    if request.user.is_superuser or content.feed.moderator_group in request.user.groups.all():
        can_delete = True
        can_moderate = True
    else:
        can_delete = False
        can_moderate = False
    if content.user == request.user:
        can_delete = True
    image = Image.objects.filter(content=content)
    return render(request, 'app/content_view.html',
                  {"content": content, "images": image, "form": form, "can_delete": can_delete,
                   "can_moderate": can_moderate})


def approve_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    if not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all():  # Modo ou SuperAd
        return utils.denied(request)
    content.state = 'A'
    content.user_moderator = request.user
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
            return utils.denied(request)
        message = form.cleaned_data['reason']
        content.state = 'R'
        content.user_moderator = request.user
        content.reject_reason = message
        content.save()

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


def delete_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    if not request.user.is_superuser and content.feed.moderator_group not in request.user.groups.all() and content.user != request.user:
        return utils.denied(request)
    pk_feed = content.feed.pk
    content.delete()
    return redirect(reverse("content_list", args=[pk_feed]))


def json_screen(request, token_screen):
    json = []
    screen = get_object_or_404(Screen, token=token_screen)
    screen.date_last_call = timezone.now()  # On enregistre l'appel au json (pour le monitoring)
    screen.save()
    # Si l'écran est éteint et qu'il est censé l'être, on affiche une image fixe pour éviter de faire travailler le proc
    if screen.screen_is_off:
        image = {'type': 'off', 'content': "", 'duration': 120}
        json.append(image)
        return JsonResponse(json, safe=False)
    urgent = Subscription.objects.filter(subscription_type="U").filter(screen=screen)
    json = utils.json_append(urgent)
    if len(json) == 0:
        subscription = Subscription.objects.filter(subscription_type="N").filter(screen=screen)
        json = utils.json_append(subscription)
    return JsonResponse(json, safe=False)


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
        screen = Screen.objects.order_by("name", "place_group")
    else:
        screen = Screen.objects.filter(hidden=False).order_by("name", "place_group")
    return render(request, 'app/list_screen.html', {"screen": screen})


def view_screen(request, pk_screen):
    screen = get_object_or_404(Screen, pk=pk_screen)
    if not request.user.is_superuser and screen.hidden and screen.owner_group not in request.user.groups.all():
        return utils.denied(request)
    urgent = Subscription.objects.filter(screen=screen).filter(subscription_type="U").order_by("-priority")
    normal = Subscription.objects.filter(screen=screen).filter(subscription_type="N").order_by("-priority")
    hour = Hour.objects.filter(hour_group=screen.place_group.hour_group).order_by("day", 'first_hour')
    if request.user.is_superuser or screen.owner_group in request.user.groups.all():
        can_admin = True
    else:
        can_admin = False
    return render(request, 'app/view_screen.html',
                  {"screen": screen, "urgent": urgent, "normal": normal, "hour_list": hour, "can_admin": can_admin})


def delete_subscription(request, pk_sub):
    subscription = get_object_or_404(Subscription, pk=pk_sub)
    if not request.user.is_superuser and subscription.screen.owner_group not in request.user.groups.all():
        return utils.denied(request)
    subscription.delete()
    return redirect(reverse("view_screen", args=[subscription.screen.pk]))


def up_subscription(request, pk_sub):
    subscription = get_object_or_404(Subscription, pk=pk_sub)
    if not request.user.is_superuser and subscription.screen.owner_group not in request.user.groups.all():
        return utils.denied(request)
    if subscription.priority < 10:
        subscription.priority += 1
        subscription.save()
    return redirect(reverse("view_screen", args=[subscription.screen.pk]))


def down_subscription(request, pk_sub):
    subscription = get_object_or_404(Subscription, pk=pk_sub)
    if not request.user.is_superuser and subscription.screen.owner_group not in request.user.groups.all():
        return utils.denied(request)
    if subscription.priority > 1:
        subscription.priority -= 1
        subscription.save()
    return redirect(reverse("view_screen", args=[subscription.screen.pk]))


def add_subscription(request, pk_screen, type_sub):
    screen = get_object_or_404(Screen, pk=pk_screen)
    if not request.user.is_superuser and screen.owner_group not in request.user.groups.all():
        return utils.denied(request)
    form = SubscriptionForm(request.POST or None)
    if type_sub == "U":
        form.fields["priority"].initial = 1
        form.fields["priority"].widget = HiddenInput()
    if not request.user.is_superuser:
        form.fields["feed"].queryset = Feed.objects.filter(submitter_group__in=request.user.groups.all())
    actuel = Subscription.objects.filter(screen=screen).filter(subscription_type=type_sub)
    print(actuel)
    form.fields["feed"].queryset = form.fields["feed"].queryset.exclude(pk__in=[feed.feed.pk for feed in actuel])
    if form.is_valid():
        if not type_sub == "N" and not type_sub == "U":
            return utils.denied(request)
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
            last_monitoring = timezone.now() - timezone.timedelta(minutes=20)
            if screen.date_last_call > last_monitoring:
                return HttpResponse(screen.screen_need_on)
            else:
                mail_admins("Reboot screen", "L'écran " + str(
                    screen.name) + " a reçu une consigne de redemarrage. Dernier call : " + str(screen.date_last_call))
                return HttpResponse(3)
        return HttpResponse(300)
    except:
        return HttpResponse(300)  # Si l'écran n'est pas encore enregistré


def screen_monitoring(request):
    if not request.user.is_superuser:
        return utils.denied(request)
    screen = Screen.objects.order_by("name", "place_group")
    return render(request, "app/screen_monitoring.html", {"screen": screen})


def screen_monitoring_get_control_mode(request, token):
    try:
        screen = Screen.objects.get(token=token)
        return HttpResponse(screen.screen_control_type)
    except:
        return HttpResponse(1)


class ContentUpdate(UpdateView):
    model = Content
    fields = ['begin_date', 'end_date', 'duration', 'content_url']
    template_name = 'registration/user_update.html'
    # success_url = reverse_lazy('home', args=[self.request])


def restaurant_add(request):
    form = RestaurantForm(request.POST or None)
    group_restaurant = Group.objects.get(pk=settings.RESTAURANTS_GROUP_PK)
    if not request.user.is_superuser and group_restaurant not in request.user.groups.all():
        return utils.denied(request)
    if form.is_valid():
        for i in ["midi1", "midi2", "midi3", "midi4", "midi5"]:
            if i in request.FILES:
                content = Content()
                content.name = i + " -  " + str(form.cleaned_data["date"])
                content.user = request.user
                content.content_type = "I"
                content.content_url = "image"
                content.state = "P"
                content.duration = 7
                content.begin_date = timezone.datetime.combine(form.cleaned_data["date"],
                                                               timezone.datetime(1, 1, 1, hour=10).time())
                content.end_date = timezone.datetime.combine(form.cleaned_data["date"],
                                                             timezone.datetime(1, 1, 1, hour=14).time())
                content.feed = Feed.objects.get(pk=settings.RESTAURANTS_FEED_PK)
                validator(request.FILES[i])
                content.save()
                utils.save_image(request.FILES[i], content, request.user)
        for i in ["soir1", "soir2", "soir3", "soir4", "soir5"]:
            if i in request.FILES:
                content = Content()
                content.name = i + " -  " + str(form.cleaned_data["date"])
                content.user = request.user
                content.content_type = "I"
                content.content_url = "image"
                content.state = "P"
                content.duration = 7
                content.begin_date = timezone.datetime.combine(form.cleaned_data["date"],
                                                               timezone.datetime(1, 1, 1, hour=14).time())
                content.end_date = timezone.datetime.combine(form.cleaned_data["date"],
                                                             timezone.datetime(1, 1, 1, hour=20).time())
                content.feed = Feed.objects.get(pk=settings.RESTAURANTS_FEED_PK)
                validator(request.FILES[i])
                content.save()
                utils.save_image(request.FILES[i], content, request.user)
        return redirect(reverse("content_list", args=[content.feed.pk]))
    else:
        return render(request, 'app/restaurants.html', {"form": form})
