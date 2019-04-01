from bootstrap_datepicker_plus import DateTimePickerInput, DatePickerInput
from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django_registration.forms import RegistrationForm

from .models import Content, Subscription


class UserProfileRegistrationForm(RegistrationForm):
    first_name = forms.CharField(label='Prénom', required=True)
    last_name = forms.CharField(label='Nom', required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmation du mot de passe")
    captcha = ReCaptchaField(label="Êtes-vous un robot ?")

    class Meta:
        model = User
        fields = (User.USERNAME_FIELD, "email", 'first_name', 'last_name')
        help_texts = {'username': ""}


class ContentFormImage(forms.ModelForm):
    file = forms.FileField(required=False, label="Fichier à afficher (.png, .jpg, .jpeg, .pdf)")

    class Meta:
        now = timezone.now()
        today = timezone.datetime.combine(now, timezone.datetime(1, 1, 1, hour=6).time())
        end = timezone.datetime.combine(now + timezone.timedelta(days=7), timezone.datetime(1, 1, 1, hour=23).time())
        model = Content
        fields = ['name', 'begin_date', 'end_date', 'feed', 'duration']
        widgets = {
            'begin_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": today.isoformat(),
                "maxDate": (now + timezone.timedelta(days=30)).isoformat(),
                "defaultDate": today.isoformat(),
            }),
            'end_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": today.isoformat(),
                "maxDate": (now + timezone.timedelta(days=37)).isoformat(),
                "defaultDate": end.isoformat()
            }),  # specify date-frmat
        }


class ContentFormYoutube(forms.ModelForm):
    class Meta:
        now = timezone.now()
        today = timezone.datetime.combine(now, timezone.datetime(1, 1, 1, hour=6).time())
        end = timezone.datetime.combine(now + timezone.timedelta(days=7), timezone.datetime(1, 1, 1, hour=23).time())
        model = Content
        fields = ['name', 'begin_date', 'end_date', 'content_url', 'feed', 'duration']
        labels = {"content_url": "ID Vidéo Youtube"}
        widgets = {
            'begin_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": today.isoformat(),
                "maxDate": (now + timezone.timedelta(days=30)).isoformat(),
                "defaultDate": today.isoformat(),
            }),
            'end_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": today.isoformat(),
                "maxDate": (now + timezone.timedelta(days=37)).isoformat(),
                "defaultDate": end.isoformat()
            }),  # specify date-frmat
        }


class ContentFormUrl(forms.ModelForm):
    class Meta:
        now = timezone.now()
        today = timezone.datetime.combine(now, timezone.datetime(1, 1, 1, hour=6).time())
        end = timezone.datetime.combine(now + timezone.timedelta(days=7), timezone.datetime(1, 1, 1, hour=23).time())
        model = Content
        fields = ['name', 'begin_date', 'end_date', 'content_url', 'feed', 'duration']
        labels = {"content_url": "Lien page web (HTTPS uniquement)"}
        widgets = {
            'begin_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": today.isoformat(),
                "maxDate": (now + timezone.timedelta(days=30)).isoformat(),
                "defaultDate": today.isoformat(),
            }),
            'end_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": today.isoformat(),
                "maxDate": (now + timezone.timedelta(days=37)).isoformat(),
                "defaultDate": end.isoformat()
            }),  # specify date-frmat
        }


class ContentUpdateForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['begin_date', 'end_date', 'duration']
        labels = {"content_url": "Lien page web HTTPS ou ID Vidéo"}
        widgets = {
            'begin_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
            }),
            'end_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
            }),  # specify date-frmat
        }


class RejectContentForm(forms.Form):
    reason = forms.CharField(label="Motif du refus", help_text="Envoyé par email à l'utilisateur")


class ScreenMonitoringEndpoint(forms.Form):
    token = forms.CharField(required=True, max_length=32)
    temperature = forms.FloatField(required=False)
    load = forms.CharField(required=False)
    fs_ro = forms.BooleanField(required=False)
    tv_screen_on = forms.BooleanField(required=False)
    hostname = forms.CharField(required=True)
    ip = forms.GenericIPAddressField(required=True)


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        exclude = ('screen', 'subscription_type')


class RestaurantForm(forms.Form):
    now = timezone.now()
    date = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y', options={
        "showClose": False,
        "showClear": False,
        "showTodayButton": False,
        "locale": "fr",
        "minDate": now.isoformat(),
        "defaultDate": now.isoformat(),
    }))
    midi1 = forms.FileField(required=False, label="")
    midi2 = forms.FileField(required=False, label="")
    midi3 = forms.FileField(required=False, label="")
    midi4 = forms.FileField(required=False, label="")
    midi5 = forms.FileField(required=False, label="")
    soir1 = forms.FileField(required=False, label="")
    soir2 = forms.FileField(required=False, label="")
    soir3 = forms.FileField(required=False, label="")
    soir4 = forms.FileField(required=False, label="")
    soir5 = forms.FileField(required=False, label="")
