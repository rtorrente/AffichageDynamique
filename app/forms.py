from django import forms
from .models import Content

class ContentFormImage(forms.ModelForm):
    file = forms.FileField(required=False)
    class Meta:
        model = Content
        exclude = ('user', 'content_type', 'content_url', 'state', 'is_valid')

