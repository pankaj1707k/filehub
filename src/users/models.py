from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField("email", unique=True)
    name = models.CharField("name", max_length=256, blank=True, null=True)
