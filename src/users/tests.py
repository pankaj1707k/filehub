from django.conf import settings
from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAuthTest(TestCase):
    """
    Tests for `AuthenticationBackend`.
    """

    def setUp(self):
        self.testuser = User.objects.create(username="testuser0", email="tu0@test.com")
        self.testuser.set_password("testing@321")
        self.testuser.save()

    def test_username_login(self):
        self.assertFalse(get_user(self.client).is_authenticated)
        self.client.login(username="testuser0", password="testing@321")
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_email_login(self):
        self.assertFalse(get_user(self.client).is_authenticated)
        self.client.login(username="tu0@test.com", password="testing@321")
        self.assertTrue(get_user(self.client).is_authenticated)

    def tearDown(self):
        self.client.logout()
        self.testuser.delete()


class UserRegisterTest(TestCase):
    """
    Tests for user registration.
    """

    def setUp(self):
        self.url = reverse("register")
        self.template_name = "register.html"
        self.testuser = {
            "username": "testuser",
            "email": "tu@test.com",
            "password1": "asd@lkj123",
            "password2": "asd@lkj123",
        }

    def test_render_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template_name)

    def test_register_success(self):
        response = self.client.post(self.url, self.testuser)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
        self.assertTrue(
            User.objects.filter(username=self.testuser["username"]).exists()
        )

    def test_register_success_redirect(self):
        response = self.client.post(self.url, self.testuser, follow=True)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
