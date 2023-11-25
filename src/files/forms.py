from django.forms import ModelForm

from files.models import Directory, File


class FileForm(ModelForm):
    class Meta:
        model = File
        exclude = ["owner"]


class FileUpdateForm(ModelForm):
    class Meta:
        model = File
        fields = ["name"]


class DirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = "__all__"

    def is_valid(self) -> bool:
        return super().is_valid() and self.instance.name != "root"


class DirectoryUpdateForm(ModelForm):
    class Meta:
        model = Directory
        fields = ["name"]
