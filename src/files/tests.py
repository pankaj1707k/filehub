from uuid import uuid4

import urllib3
from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse

from files import views
from files.models import Directory, File
from files.storage import S3

User = get_user_model()


class S3Test(TestCase):
    """
    Tests for S3 storage client
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.storage_client = S3()
        cls.key = str(uuid4())

    def test_get_signed_url(self) -> None:
        response = self.storage_client.get_upload_url(self.key, 5)
        # just works, could be improved
        url_regex = r"https{0,1}://[a-z0-9\-\.]+:{0,1}[0-9]{0,5}/[a-z]+/[a-z0-9\-]+"
        url_regex += r"\?[a-zA-Z0-9\-&=%]"
        self.assertRegex(response, url_regex)


class SignedURLViewTest(TestCase):
    """
    Tests for `SignedURLView`
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("signed_url")
        cls.user = User.objects.create(username="testuser", email="tu@test.com")
        cls.user.set_password("testing123")
        cls.user.save()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_both_upload_download_true(self) -> None:
        response = self.client.get(self.url, {"upload": "true", "download": "true"})
        self.assertEqual(response.status_code, 400)

    def test_upload_url(self) -> None:
        response = self.client.get(self.url, {"upload": "true"})
        self.assertEqual(response.status_code, 200)

    def test_download_without_key(self) -> None:
        response = self.client.get(self.url, {"download": "true"})
        self.assertEqual(response.status_code, 400)

    def test_download_with_invalid_key(self) -> None:
        response = self.client.get(self.url, {"download": "true", "key": str(uuid4())})
        self.assertEqual(response.status_code, 404)

    def test_download_with_valid_key(self) -> None:
        file = File.objects.create(
            name="test",
            type="text/plain",
            size=1024,
            directory=Directory.objects.create(name="testdir", owner=self.user),
            owner=self.user,
        )
        response = self.client.get(self.url, {"download": "true", "key": str(file.id)})
        self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        self.client.logout()


class FileDeleteTest(TestCase):
    """
    When a file entry is deleted from the database, the corresponding file
    must be autodeleted from the object storage.
    """

    def setUp(self) -> None:
        self.user = User.objects.create(username="testuser", email="tu@test.com")
        self.user.set_password("testing123")
        self.user.save()
        self.file = File.objects.create(
            name="testfile",
            type="text/plain",
            size=1024,
            directory=Directory.objects.get(name="root", owner=self.user),
            owner=self.user,
        )
        self.storage_client = S3()
        upload_url = self.storage_client.get_upload_url(str(self.file.id), 5)
        urllib3.request(
            "PUT",
            upload_url,
            body="someplaintextdata",
            headers={"Content-Type": "text/plain"},
        )
        self.delete_url = reverse("delete_file", args=(self.file.id,))
        self.client.force_login(self.user)

    def test_file_delete(self) -> None:
        key = str(self.file.id)
        download_url = self.storage_client.get_download_url(key, 5)
        response = self.client.post(self.delete_url)
        storage_response = urllib3.request("GET", download_url)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(response.has_header("HX-Trigger"))
        self.assertEqual(storage_response.status, 404)
        self.assertEqual(get_user(self.client).storage_used, 0)


class FileCreateTest(TestCase):
    """
    Tests for file creation.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.create_url = reverse("create_file")
        cls.user = User.objects.create(username="testuser", email="tu@test.com")
        cls.user.set_password("testing123")
        cls.user.save()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_create_file(self) -> None:
        file_data = {
            "id": uuid4(),
            "name": "testfile",
            "type": "text/plain",
            "size": 100,
        }
        response = self.client.post(
            self.create_url, file_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(File.objects.filter(**file_data).exists())
        self.assertEqual(get_user(self.client).storage_used, file_data["size"])

    def test_create_file_with_invalid_size(self) -> None:
        file_data = {
            "id": uuid4(),
            "name": "testfile",
            "type": "text/plain",
            "size": 1024 * 1024 * 1024 * 2,  # 2GB (more than max storage)
        }
        response = self.client.post(
            self.create_url, file_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(File.objects.filter(**file_data).exists())
        self.assertEqual(get_user(self.client).storage_used, 0)

    def tearDown(self) -> None:
        self.client.logout()


class FileUpdateTest(TestCase):
    """
    Tests for file update.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username="testuser", email="tu@test.com")
        cls.user.set_password("testing123")
        cls.user.save()
        cls.file = File.objects.create(
            name="testfile",
            type="text/plain",
            size=1024,
            directory=Directory.objects.get(name="root", owner=cls.user),
            owner=cls.user,
        )
        cls.update_url = reverse("update_file", args=(cls.file.id,))

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_update_file(self) -> None:
        post_data = {"name": "testfileupdated"}
        response = self.client.post(self.update_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post_data["name"])
        self.assertEqual(File.objects.get(id=self.file.id).name, post_data["name"])

    def tearDown(self) -> None:
        self.client.logout()


class DirectoryCreateUpdateDeleteTest(TestCase):
    """
    Tests for create, update, delete operations for file objects
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.create_url = reverse("create_dir")
        cls.update_response_template = views.DirectoryUpdateView.template_name
        cls.user = User.objects.create(username="testuser", email="tu@test.com")
        cls.user.set_password("testing123")
        cls.user.save()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_create_directory(self) -> None:
        root_dir_id = str(Directory.objects.get(name="root", owner=self.user).id)
        post_data = {
            "name": "testdir",
            "parent_directory": root_dir_id,
            "owner": self.user.id,
        }
        response = self.client.post(self.create_url, post_data)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(response.has_header("HX-Trigger"))

    def test_update_directory(self) -> None:
        dir = Directory.objects.create(
            name="testdir",
            parent_directory=Directory.objects.get(name="root", owner=self.user),
            owner=self.user,
        )
        update_url = reverse("update_dir", args=(dir.id,))
        post_data = {"name": "testdirupdated"}
        response = self.client.post(update_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.update_response_template)
        self.assertContains(response, response.context["curr_dir"].name)

    def test_root_update_not_allowed(self) -> None:
        root = Directory.objects.get(name="root", owner=self.user)
        update_url = reverse("update_dir", args=(root.id,))
        post_data = {"name": "testdirupdated"}
        response = self.client.post(update_url, post_data)
        self.assertEqual(response.status_code, 403)

    def test_delete(self) -> None:
        dir = Directory.objects.create(
            name="testdir",
            parent_directory=Directory.objects.get(name="root", owner=self.user),
            owner=self.user,
        )
        delete_url = reverse("delete_dir", args=(dir.id,))
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(response.has_header("HX-Trigger"))

    def test_root_delete_not_allowed(self) -> None:
        root = Directory.objects.get(name="root", owner=self.user)
        update_url = reverse("delete_dir", args=(root.id,))
        response = self.client.post(update_url)
        self.assertEqual(response.status_code, 403)

    def tearDown(self) -> None:
        self.client.logout()


class SearchContentTest(TestCase):
    """
    Tests for search functionality.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.search_url = reverse("search_content")
        cls.user = User.objects.create(username="testuser", email="tu@test.com")
        cls.user.set_password("testing123")
        cls.user.save()
        root_dir = Directory.objects.get(name="root", owner=cls.user)
        cls.test_dir = Directory.objects.create(
            name="testdir", parent_directory=root_dir, owner=cls.user
        )
        cls.test_file = File.objects.create(
            name="testfile",
            type="text/plain",
            size=1024,
            directory=root_dir,
            owner=cls.user,
        )

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_query_param_missing(self) -> None:
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 400)

    def test_query_empty(self) -> None:
        response = self.client.get(self.search_url, {"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_file.name)
        self.assertContains(response, self.test_dir.name)

    def test_search_with_full_name(self) -> None:
        response = self.client.get(self.search_url, {"q": "testfile"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_file.name)

    def test_search_with_partial_name(self) -> None:
        response = self.client.get(self.search_url, {"q": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_file.name)
        self.assertContains(response, self.test_dir.name)

    def tearDown(self) -> None:
        self.client.logout()


class FileStatsTest(TestCase):
    """
    Tests for file statistics view.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.stats_url = reverse("file_stats")
        cls.user = User.objects.create(username="testuser", email="tu@test.com")
        cls.user.set_password("testing123")
        cls.user.save()
        root_dir = Directory.objects.get(name="root", owner=cls.user)
        cls.test_file = File.objects.create(
            name="testfile",
            type="image/png",
            size=1024,
            directory=root_dir,
            owner=cls.user,
        )

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_stats(self) -> None:
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("stats", response.context)
        for file_type in views.FileStatsView.file_types:
            self.assertIn(file_type[1], response.context["stats"])
        self.assertIn("Other", response.context["stats"])
        self.assertEqual(response.context["stats"]["Image"]["count"], 1)
        self.assertEqual(response.context["stats"]["Image"]["size"], 1)
        self.assertEqual(response.context["stats"]["Image"]["unit"], "KB")

    def tearDown(self) -> None:
        self.client.logout()
