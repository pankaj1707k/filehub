from django.urls import path

from files import views

urlpatterns = [
    path("get-signed-url/", views.SignedURLView.as_view(), name="signed-url"),
]
