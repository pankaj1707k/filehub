from django.db.models.signals import pre_delete
from django.dispatch import receiver

from files.models import File
from files.storage import S3


@receiver(pre_delete, sender=File)
def delete_file(instance: File, *args, **kwargs) -> None:
    S3().delete_file(str(instance.id))
