from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm

User = get_user_model()


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "name")
