from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from files.models import Directory, File
from files.storage import S3

User = get_user_model()


class S3Test(TestCase):
    """
    Tests for S3 storage client
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
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
    def setUpClass(cls) -> None:
        super().setUpClass()
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

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.user.delete()


class FileCreateUpdateDeleteTest(TestCase):
    """
    Tests for create, update, delete operations for file objects
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.create_url = reverse("create_file")
        cls.user = User.objects.create(username="testuser", email="tu@test.com")
        cls.user.set_password("testing123")
        cls.user.save()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_create_file(self) -> None:
        response = self.client.post(
            self.create_url,
            {"id": uuid4(), "name": "testfile", "type": "text/plain", "size": 100},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def tearDown(self) -> None:
        self.client.logout()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.user.delete()
