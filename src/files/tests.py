from uuid import uuid4

from django.test import TestCase

from files.storage import S3


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
