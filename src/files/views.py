import json
from typing import Any
from uuid import uuid4

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.views.generic import TemplateView

from files.forms import DirectoryForm, FileForm
from files.models import Directory, File
from files.storage import S3
from users.mixins import AuthenticatedRequestMixin


class DirectoryView(AuthenticatedRequestMixin, TemplateView):
    """
    Render the contents of a directory for an authenticated user.
    """

    template_name = "private/dashboard/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        arg_dir = Directory.objects.get(id=kwargs.get("id"))
        context["dirs"] = Directory.objects.filter(parent_directory=arg_dir)
        context["files"] = File.objects.filter(directory=arg_dir)
        return context


class SignedURLView(AuthenticatedRequestMixin, View):
    """
    Generate a signed URL for client-side object storage access
    """

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        upload = request.GET.get("upload", "").lower() == "true"
        download = request.GET.get("download", "").lower() == "true"

        if not (upload ^ download):
            return JsonResponse(
                {"error": "exactly one of upload and download must be true"},
                status=400,
            )

        if upload:
            key = str(uuid4())
            url = S3().get_upload_url(key)
            return JsonResponse({"url": url, "key": key}, status=200)

        key = request.GET.get("key")
        if not key:
            return JsonResponse({"error": "key not provided"}, status=400)
        if not File.objects.filter(id=key).exists():
            return JsonResponse({"error": "no file found with given key"}, status=404)

        url = S3().get_download_url(key)
        return JsonResponse({"url": url, "key": key}, status=200)


class FileCreateView(AuthenticatedRequestMixin, View):
    """
    Create a file metadata object. The request must have `application/json`
    content type.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        file_form = FileForm(json.loads(request.body))
        if file_form.is_valid():
            file_form.instance.owner = request.user
            file_form.save()
            return HttpResponse(status=201)
        return JsonResponse(file_form.errors, status=400)


class FileDirListView(AuthenticatedRequestMixin, TemplateView):
    """
    Return rendered template for file and directory list.
    """

    template_name = "private/dashboard/dirs_and_files.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        dir_id = self.request.GET.get("parent_directory")
        context["dirs"] = Directory.objects.filter(
            parent_directory__id=dir_id, owner=self.request.user
        )
        context["files"] = File.objects.filter(
            directory__id=dir_id, owner=self.request.user
        )
        context["curr_dir"] = dir_id
        return context


class DirectoryCreateView(AuthenticatedRequestMixin, View):
    """
    Create a new directory.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = DirectoryForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "newDirCreated"
            return response
        return JsonResponse(form.errors, status=400)
