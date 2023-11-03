import json
from typing import Any
from uuid import uuid4

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from files import forms
from files.models import Directory, File
from files.storage import S3
from files.utils import get_size_in_largest_unit
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
        context["curr_dir"] = arg_dir
        context["root"] = Directory.objects.get(name="root", owner=self.request.user)
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
        request_data = json.loads(request.body)
        file_form = forms.FileForm(request_data)
        if file_form.is_valid():
            # ensure user has enough storage space
            if (
                request.user.storage_used + file_form.instance.size
                > request.user.max_storage
            ):
                return JsonResponse(
                    {
                        "error": (
                            f"File is too large. You have "
                            f"{request.user.max_storage - request.user.storage_used} "
                            f"bytes left."
                        )
                    },
                    status=400,
                )
            data = file_form.cleaned_data
            data["owner"] = request.user
            data["id"] = request_data["id"]
            File.objects.create(**data)
            setattr(
                request.user,
                "storage_used",
                getattr(request.user, "storage_used") + data["size"],
            )
            request.user.save()
            return HttpResponse(status=201)
        return JsonResponse(file_form.errors, status=400)


class FileDetailView(AuthenticatedRequestMixin, TemplateView):
    """
    Render the details of a file.
    """

    template_name = "private/dashboard/file_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        file = File.objects.get(id=kwargs.get("id"))
        context["file"] = file
        context["root"] = Directory.objects.get(name="root", owner=self.request.user)
        return context


class FileUpdateView(AuthenticatedRequestMixin, View):
    """
    Rename a file.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        file = File.objects.get(id=kwargs.get("id"))
        form = forms.FileUpdateForm(request.POST, instance=file)
        if form.is_valid():
            form.save()
            return HttpResponse(form.instance.name, status=200)
        return JsonResponse(form.errors, status=400)


class FileDeleteView(AuthenticatedRequestMixin, View):
    """
    Delete a file and trigger a component reload.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        file = File.objects.get(id=kwargs.get("id"))
        file.delete()
        setattr(
            request.user,
            "storage_used",
            max(getattr(request.user, "storage_used") - file.size, 0),
        )
        request.user.save()
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "contentChange"
        return response


class FileDirListView(AuthenticatedRequestMixin, TemplateView):
    """
    Return rendered template for file and directory list.
    """

    template_name = "private/dashboard/dirs_and_files.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        dir_id = self.request.GET.get("parent_directory")
        arg_dir = Directory.objects.get(id=dir_id)
        context["dirs"] = Directory.objects.filter(
            parent_directory=arg_dir, owner=self.request.user
        )
        context["files"] = File.objects.filter(
            directory=arg_dir, owner=self.request.user
        )
        context["curr_dir"] = arg_dir
        return context


class DirectoryCreateView(AuthenticatedRequestMixin, View):
    """
    Create a new directory.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = forms.DirectoryForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "contentChange"
            return response
        return JsonResponse(form.errors, status=400)


class DirectoryUpdateView(AuthenticatedRequestMixin, View):
    """
    Rename a directory.
    """

    http_method_names = ["post"]
    template_name = "private/dashboard/dir_title.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        dir = Directory.objects.get(id=kwargs.get("id"))
        # do not allow root directory to be renamed
        if dir.name == "root":
            return HttpResponse(status=403)
        form = forms.DirectoryUpdateForm(request.POST, instance=dir)
        if form.is_valid():
            form.save()
            context = {"curr_dir": form.instance}
            return render(request, self.template_name, context)
        return JsonResponse(form.errors, status=400)


class DirectoryDeleteView(AuthenticatedRequestMixin, View):
    """
    Delete a directory and trigger a component reload.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        dir = Directory.objects.get(id=kwargs.get("id"))
        # do not allow deletion of root directory
        if dir.name == "root":
            return HttpResponse(status=403)
        dir.delete()
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "contentChange"
        return response


class SearchView(AuthenticatedRequestMixin, TemplateView):
    """
    Search for files and directories.
    """

    template_name = "private/dashboard/dirs_and_files.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        query = request.GET.get("q")
        if query is None:
            return JsonResponse({"error": "query not provided"}, status=400)
        filter_params = {"name__icontains": query, "owner": request.user}
        dirs = list(Directory.objects.filter(**filter_params).exclude(name="root"))
        files = list(File.objects.filter(**filter_params))
        context = super().get_context_data(**kwargs)
        context.update({"dirs": dirs, "files": files})
        return render(request, self.template_name, context)


class FileStatsView(AuthenticatedRequestMixin, TemplateView):
    """
    Render statistics for each file type.
    """

    template_name = "private/dashboard/file_stats.html"

    # type, template string
    file_types = [
        ("image", "Image"),
        ("pdf", "PDF"),
        ("audio", "Audio"),
        ("video", "Video"),
    ]

    # icons for each file type
    file_icons = {
        "image": "fa-file-image",
        "pdf": "fa-file-pdf",
        "audio": "fa-file-audio",
        "video": "fa-file-video",
        "other": "fa-file",
    }

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        all_files = File.objects.filter(owner=self.request.user)
        file_stats_by_type = {}
        total_size = total_count = 0

        for type, template_string in self.file_types:
            files = all_files.filter(type__icontains=type)
            count = files.count()
            total_count += count
            type_size = sum(file.size for file in files)
            total_size += type_size
            size_unit, type_size = get_size_in_largest_unit(type_size)
            file_stats_by_type[template_string] = {
                "count": count,
                "size": type_size,
                "unit": size_unit,
                "icon": self.file_icons[type],
            }

        # set stats for "other" file types
        other_count = all_files.count() - total_count
        other_size = sum(file.size for file in all_files) - total_size
        size_unit, other_size = get_size_in_largest_unit(other_size)
        file_stats_by_type["Other"] = {
            "count": other_count,
            "size": other_size,
            "unit": size_unit,
            "icon": self.file_icons["other"],
        }

        context["stats"] = file_stats_by_type
        return context
