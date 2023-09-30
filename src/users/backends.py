from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class AuthBackend(ModelBackend):
    """
    Authenticate using either username or email combined with the password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if password is None:
            return
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            # Derived from super().authenticate()
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
