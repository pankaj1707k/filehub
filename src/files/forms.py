from django.forms import ModelForm

from files.models import File


class FileForm(ModelForm):
    class Meta:
        model = File
        exclude = ["owner"]
