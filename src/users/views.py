from django.shortcuts import redirect
from django.views import generic


class HomeView(generic.TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("dashboard")
        return super().get(request, *args, **kwargs)


class LoginView(generic.TemplateView):
    template_name = "login.html"
