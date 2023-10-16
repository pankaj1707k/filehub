from django.http import HttpRequest, HttpResponse, JsonResponse


class AuthenticatedRequestMixin:
    """
    Verify that the current user is authenticated
    """

    permission_denied_message = "Anonymous user not allowed"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return JsonResponse({"error": self.permission_denied_message}, status=403)
        return super().dispatch(request, *args, **kwargs)
