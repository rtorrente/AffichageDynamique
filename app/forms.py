from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.utils import timezone

from .models import Content


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

