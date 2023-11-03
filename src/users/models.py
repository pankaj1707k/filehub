from django.contrib.auth.models import AbstractUser
from django.db import models

DEFAULT_MAX_STORAGE_PER_USER = 1024 * 1024 * 1024 * 1  # 1GB


class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField("email", unique=True)
    name = models.CharField("name", max_length=256, blank=True, null=True)
    max_storage = models.PositiveBigIntegerField(
        "max storage", default=DEFAULT_MAX_STORAGE_PER_USER, blank=True
    )
    storage_used = models.PositiveBigIntegerField("storage used", default=0, blank=True)

    def get_full_name(self):
        return self.name
