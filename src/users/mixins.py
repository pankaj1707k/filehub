from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse

from files.models import Directory


class AuthenticatedRequestMixin:
    """
    Verify that the current user is authenticated
    """

    permission_denied_message = "Anonymous user not allowed"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return JsonResponse({"error": self.permission_denied_message}, status=403)
        return super().dispatch(request, *args, **kwargs)


class AuthenticatedRedirectMixin:
    """
    Redirect authenticated user to main dashboard from 'home', 'login',
    'register' etc.
    """

    def get_success_url(self) -> str:
        id = str(Directory.objects.get(name="root", owner=self.request.user).id)
        return reverse(
            settings.LOGIN_REDIRECT_URL,
            args=(id,),
        )
