from django.contrib.auth import get_user, get_user_model
from django.test import TestCase

User = get_user_model()


class UserAuthTest(TestCase):
    def setUp(self):
        self.testuser = User.objects.create(username="testuser0", email="tu0@test.com")
        self.testuser.set_password("testing@321")
        self.testuser.save()

    def test_username_login(self):
        self.assertFalse(get_user(self.client).is_authenticated)
        self.client.login(login="testuser0", password="testing@321")
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_email_login(self):
        self.assertFalse(get_user(self.client).is_authenticated)
        self.client.login(login="tu0@test.com", password="testing@321")
        self.assertTrue(get_user(self.client).is_authenticated)

    def tearDown(self):
        self.client.logout()
        self.testuser.delete()
