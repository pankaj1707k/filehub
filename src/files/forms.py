from django.forms import ModelForm

from files.models import Directory, File


class FileForm(ModelForm):
    class Meta:
        model = File
        exclude = ["owner"]


class DirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = "__all__"
