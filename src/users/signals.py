from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from files.models import Directory

User = get_user_model()


@receiver(post_save, sender=User)
def create_root_dir(instance: User, created: bool, *args, **kwargs) -> None:
    if created:
        Directory.objects.create(name="root", owner=instance)
