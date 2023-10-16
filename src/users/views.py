from typing import Any

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from files.models import Directory, File
from users import forms
from users.mixins import AuthenticatedRequestMixin


class HomeView(TemplateView):
    """
    Render the landing page. Redirect logged in users to the dashboard.
    """

    template_name = "public/home.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request, *args, **kwargs)


class LoginView(auth_views.LoginView):
    """
    Render the login form and handle the login action. Redirect logged in
    users to the dashboard.
    """

    template_name = "public/login.html"
    redirect_authenticated_user = True


class RegisterView(FormView):
    """
    Render the registration form and handle user registration. Successfully
    registered users are immediately logged in and redirected to the dashboard.
    """

    template_name = "public/register.html"
    form_class = forms.UserCreationForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    """
    Log out the user and redirect to the landing page.
    """

    template_name = None


class DashboardView(AuthenticatedRequestMixin, TemplateView):
    """
    Render the dashboard for an authenticated user.
    """

    template_name = "private/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["dirs"] = Directory.objects.filter(
            parent_directory__id=None, owner=self.request.user
        )
        context["files"] = File.objects.filter(
            directory__id=None, owner=self.request.user
        )
        return context


class PasswordResetView(auth_views.PasswordResetView):
    """
    Request for a password reset
    """

    template_name = "public/password_reset/request_form.html"


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    """
    Show 'request sent to email' message
    """

    template_name = "public/password_reset/request_sent.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Confirm and update new password
    """

    template_name = "public/password_reset/confirm.html"


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """
    Show 'password reset success' message
    """

    template_name = "public/password_reset/complete.html"
