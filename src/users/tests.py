from django.conf import settings
from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.test import TestCase
from django.urls import reverse

from users import forms, views

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
        cls.login_template = "public/login.html"
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
        self.assertRedirects(
            response,
            reverse(
                settings.LOGIN_REDIRECT_URL,
                args=(str(self.testuser.dirs.get(name="root").id),),
            ),
        )

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
        cls.register_template = "public/register.html"
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
        user = User.objects.get(username=self.testuser["username"])
        root_id = str(user.dirs.get(name="root").id)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL, args=(root_id,)),
        )


class UserLogoutTest(TestCase):
    """
    Tests for log out and consequent redirect.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testuser = User.objects.create(username="testuser", email="tu@test.com")
        cls.testuser.set_password("testing@321")
        cls.testuser.save()
        cls.logout_url = reverse("logout")

    def test_logout_success_redirect(self):
        self.client.force_login(self.testuser)
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.testuser.delete()


class UserUpdateTest(TestCase):
    """
    Tests for updating user information.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.testuser = User.objects.create(username="testuser", email="tu@test.com")
        cls.testuser.set_password("testing@321")
        cls.testuser.save()
        cls.url = reverse("user_update")
        cls.form_class = forms.UserUpdateForm
        cls.template_name = views.UserUpdateView.template_name

    def setUp(self) -> None:
        self.client.force_login(self.testuser)

    def test_get_empty_form(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], self.form_class)
        self.assertContains(response, self.testuser.username)

    def test_post_update(self) -> None:
        post_data = {
            "username": "testuserupdated",
            "email": "tu@update.com",
            "name": "test user",
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], self.form_class)
        for updated_value in post_data.values():
            self.assertContains(response, updated_value)

    def tearDown(self) -> None:
        self.client.logout()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.testuser.delete()


class PasswordChangeTest(TestCase):
    """
    Tests for changing user password.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.testuser = User.objects.create(username="testuser", email="tu@test.com")
        cls.testuser.set_password("testing@321")
        cls.testuser.save()
        cls.url = reverse("password_update")
        cls.form_class = PasswordChangeForm
        cls.template_name = views.PasswordUpdateView.template_name

    def setUp(self) -> None:
        self.client.force_login(self.testuser)

    def test_get_empty_form(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], self.form_class)

    def test_post_update(self) -> None:
        post_data = {
            "old_password": "testing@321",
            "new_password1": "asd@lkj123",
            "new_password2": "asd@lkj123",
        }
        response = self.client.post(self.url, post_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertFalse(form.user.check_password(post_data["old_password"]))
        self.assertTrue(form.user.check_password(post_data["new_password1"]))

    def tearDown(self) -> None:
        self.client.logout()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.testuser.delete()
