from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views import generic

from users import forms


class HomeView(generic.TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("dashboard")
        return super().get(request, *args, **kwargs)


class LoginView(generic.TemplateView):
    template_name = "login.html"
    form_class = forms.UserLoginForm

    def get(self, request):
        form = self.form_class()
        context = self.get_context_data()
        context["form"] = form
        return render(request, self.template_name, context)

    def post_form_valid(self, request, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        return authenticate(request, username=username, password=password)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = self.post_form_valid(request, form)
            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid credentials")
        context = self.get_context_data()
        context["form"] = form
        return render(request, self.template_name, context)


class RegisterView(LoginView):
    template_name = "register.html"
    form_class = forms.UserRegisterForm

    def post_form_valid(self, request, form):
        return form.save()
