from bootstrap_datepicker_plus import DateTimePickerInput
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
        model = Content
        exclude = ('user', 'content_type', 'content_url', 'state', 'is_valid')
        widgets = {
            'begin_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": now.isoformat(),
                "maxDate": (now + timezone.timedelta(days=30)).isoformat(),
                "defaultDate":now.isoformat(),
                 }),
            'end_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": now.isoformat(),
                "maxDate": (now + timezone.timedelta(days=37)).isoformat(),
                "defaultDate":(now+timezone.timedelta(days=7)).isoformat()
                 }),  # specify date-frmat
        }


class ContentFormYoutube(forms.ModelForm):
    class Meta:
        now = timezone.now()
        model = Content
        exclude = ('user', 'content_type', 'state', 'is_valid')
        labels = {"content_url": "ID Vidéo Youtube"}
        widgets = {
            'begin_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": now.isoformat(),
                "maxDate": (now + timezone.timedelta(days=30)).isoformat(),
                "defaultDate": now.isoformat(),
            }),
            'end_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": now.isoformat(),
                "maxDate": (now + timezone.timedelta(days=37)).isoformat(),
                "defaultDate": (now + timezone.timedelta(days=7)).isoformat()
            }),  # specify date-frmat
        }


class ContentFormUrl(forms.ModelForm):
    class Meta:
        now = timezone.now()
        model = Content
        exclude = ('user', 'content_type', 'state', 'is_valid')
        labels = {"content_url": "Lien page web (HTTPS uniquement)"}
        widgets = {
            'begin_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": now.isoformat(),
                "maxDate": (now + timezone.timedelta(days=30)).isoformat(),
                "defaultDate": now.isoformat(),
            }),
            'end_date': DateTimePickerInput(format='%d/%m/%Y %H:%M', options={
                "showClose": False,
                "showClear": False,
                "showTodayButton": False,
                "locale": "fr",
                "minDate": now.isoformat(),
                "maxDate": (now + timezone.timedelta(days=37)).isoformat(),
                "defaultDate": (now + timezone.timedelta(days=7)).isoformat()
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
