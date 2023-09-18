from django.contrib.auth import forms, get_user_model

User = get_user_model()


class UserCreationForm(forms.UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
