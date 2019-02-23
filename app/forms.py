from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.utils import timezone
from django_registration.forms import RegistrationForm

from .models import Content


class MyExtendedForm(RegistrationForm):
    first_name = forms.CharField(required=True, help_text="", label="Prénom"),
    last_name = forms.CharField(required=True, help_text="", label="Nom"),

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

class RejectContentForm(forms.Form):
    reason = forms.TextInput()


class ScreenMonitoringEndpoint(forms.Form):
    token = forms.UUIDField(required=True)
    temperature = forms.FloatField(required=False)
    load = forms.CharField(required=False)
    fs_ro = forms.BooleanField(required=False)
    tv_screen_on = forms.BooleanField(required=False)
    hostname = forms.CharField(required=True)
    ip = forms.GenericIPAddressField(required=True)
