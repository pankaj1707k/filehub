from django.urls import path

from files import views

urlpatterns = [
    path("get-signed-url/", views.SignedURLView.as_view(), name="signed_url"),
    path("f/new/", views.FileCreateView.as_view(), name="create_file"),
    path("d/children/", views.FileDirListView.as_view(), name="list_children"),
    path("d/new/", views.DirectoryCreateView.as_view(), name="create_dir"),
    path("d/<uuid:id>/", views.DirectoryView.as_view(), name="dir_contents"),
    path("d/<uuid:id>/update/", views.DirectoryUpdateView.as_view(), name="update_dir"),
]
