from django import forms
from .models import Content

class ContentFormImage(forms.ModelForm):
    #age = forms.IntegerField()
    #comment = forms.CharField(widget=forms.Textarea, validators=[faq_suggestions])
    file = forms.FileField(required=False)
    class Meta:
        model = Content
        exclude = ('user', 'content_type', 'content_url', 'state')

