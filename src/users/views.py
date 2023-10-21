from typing import Any

from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import FormView, TemplateView

from users import forms
from users.mixins import AuthenticatedRedirectMixin, AuthenticatedRequestMixin


class HomeView(AuthenticatedRedirectMixin, TemplateView):
    """
    Render the landing page. Redirect logged in users to the dashboard.
    """

    template_name = "public/home.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)


class LoginView(AuthenticatedRedirectMixin, auth_views.LoginView):
    """
    Render the login form and handle the login action. Redirect logged in
    users to the dashboard.
    """

    template_name = "public/login.html"
    redirect_authenticated_user = True


class RegisterView(AuthenticatedRedirectMixin, FormView):
    """
    Render the registration form and handle user registration. Successfully
    registered users are immediately logged in and redirected to the dashboard.
    """

    template_name = "public/register.html"
    form_class = forms.UserCreationForm

    def form_valid(self, form: forms.UserCreationForm):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    """
    Log out the user and redirect to the landing page.
    """

    template_name = None


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


class SettingsView(AuthenticatedRequestMixin, TemplateView):
    """
    Render the settings page
    """

    template_name = "private/settings/settings.html"


class UserUpdateView(AuthenticatedRequestMixin, View):
    """
    Update user information excluding password.
    """

    http_method_names = ["get", "post"]
    template_name = "private/settings/general.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = forms.UserUpdateForm(instance=request.user)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = forms.UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return render(request, self.template_name, {"form": form})
        return render(request, self.template_name, {"form": form}, status=400)


class PasswordUpdateView(AuthenticatedRequestMixin, View):
    """
    Update user password by verifying old password.
    """

    http_method_names = ["get", "post"]
    template_name = "private/settings/password.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return render(
            request, self.template_name, {"form": PasswordChangeForm(request.user)}
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return render(
                request, self.template_name, {"form": PasswordChangeForm(request.user)}
            )
        return render(request, self.template_name, {"form": form})
