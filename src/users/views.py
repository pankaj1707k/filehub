from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from users import forms


class HomeView(generic.TemplateView):
    """
    Render the landing page. Redirect logged in users to the dashboard.
    """

    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request, *args, **kwargs)


class LoginView(auth_views.LoginView):
    """
    Render the login form and handle the login action. Redirect logged in
    users to the dashboard.
    """

    template_name = "login.html"
    redirect_authenticated_user = True


class RegisterView(generic.FormView):
    """
    Render the registration form and handle user registration. Successfully
    registered users are immediately logged in and redirected to the dashboard.
    """

    template_name = "register.html"
    form_class = forms.UserCreationForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class DashboardView(generic.TemplateView):
    """
    Render the dashboard for an authenticated user.
    """

    template_name = "dashboard.html"
