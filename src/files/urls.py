from django.urls import path

from files import views

urlpatterns = [
    path("get-signed-url/", views.SignedURLView.as_view(), name="signed_url"),
    path("f/new/", views.FileCreateView.as_view(), name="create_file"),
    path("f/<uuid:id>/", views.FileDetailView.as_view(), name="detail_file"),
    path("f/<uuid:id>/delete/", views.FileDeleteView.as_view(), name="delete_file"),
    path("f/<uuid:id>/update/", views.FileUpdateView.as_view(), name="update_file"),
    path("d/content/", views.FileDirListView.as_view(), name="list_contents"),
    path("d/new/", views.DirectoryCreateView.as_view(), name="create_dir"),
    path("d/<uuid:id>/", views.DirectoryView.as_view(), name="dir_contents"),
    path("d/<uuid:id>/update/", views.DirectoryUpdateView.as_view(), name="update_dir"),
    path("d/<uuid:id>/delete/", views.DirectoryDeleteView.as_view(), name="delete_dir"),
    path("search/", views.SearchView.as_view(), name="search_content"),
    path("stats/", views.FileStatsView.as_view(), name="file_stats"),
]
