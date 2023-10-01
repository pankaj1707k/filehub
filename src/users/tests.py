from django.conf import settings
from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAuthTest(TestCase):
    """
    Tests for user authentication.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testuser = User.objects.create(username="testuser0", email="tu0@test.com")
        cls.testuser.set_password("testing@321")
        cls.testuser.save()
        cls.login_template = "login.html"
        cls.login_url = reverse(settings.LOGIN_URL)

    def test_username_login(self):
        self.assertFalse(get_user(self.client).is_authenticated)
        self.client.login(username="testuser0", password="testing@321")
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_email_login(self):
        self.assertFalse(get_user(self.client).is_authenticated)
        self.client.login(username="tu0@test.com", password="testing@321")
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_render_template(self):
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, self.login_template)

    def test_login_success_redirect(self):
        login_data = {"username": "testuser0", "password": "testing@321"}
        response = self.client.post(self.login_url, login_data, follow=True)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def tearDown(self):
        self.client.logout()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.testuser.delete()


class UserRegisterTest(TestCase):
    """
    Tests for user registration.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.register_url = reverse("register")
        cls.register_template = "register.html"
        cls.testuser = {
            "username": "testuser",
            "email": "tu@test.com",
            "password1": "asd@lkj123",
            "password2": "asd@lkj123",
        }

    def test_render_template(self):
        response = self.client.get(self.register_url)
        self.assertTemplateUsed(response, self.register_template)

    def test_register_success(self):
        response = self.client.post(self.register_url, self.testuser)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.register_template)
        self.assertTrue(
            User.objects.filter(username=self.testuser["username"]).exists()
        )

    def test_register_success_redirect(self):
        response = self.client.post(self.register_url, self.testuser, follow=True)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
