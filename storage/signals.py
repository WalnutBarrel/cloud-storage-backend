from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.utils import ProgrammingError
import os

@receiver(post_migrate)
def create_storage_accounts(sender, **kwargs):
    if sender.name != "storage":
        return

    from .models import StorageAccount

    try:
        if StorageAccount.objects.exists():
            return
    except ProgrammingError:
        # Table not created yet
        return

    accounts = [
        ("Cloudinary-1", "CLOUDINARY_1_NAME", "CLOUDINARY_1_KEY", "CLOUDINARY_1_SECRET"),
        ("Cloudinary-2", "CLOUDINARY_2_NAME", "CLOUDINARY_2_KEY", "CLOUDINARY_2_SECRET"),
        ("Cloudinary-3", "CLOUDINARY_3_NAME", "CLOUDINARY_3_KEY", "CLOUDINARY_3_SECRET"),
    ]

    for name, cname, key, secret in accounts:
        if os.getenv(cname):
            StorageAccount.objects.create(
                name=name,
                cloud_name=os.getenv(cname),
                api_key=os.getenv(key),
                api_secret=os.getenv(secret),
                limit_bytes=25 * 1024 * 1024 * 1024,
            )
