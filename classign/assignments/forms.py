from django import forms
from django_summernote.fields import SummernoteTextFormField


class FileUploadForm(forms.Form):
    url = forms.URLField()


class HTMLInputForm(forms.Form):
    text = SummernoteTextFormField()
