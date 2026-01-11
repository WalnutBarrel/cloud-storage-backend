from django.apps import AppConfig
from django.db.utils import OperationalError
import os

class StorageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "storage"

    def ready(self):
        from .models import StorageAccount

        try:
            if StorageAccount.objects.count() == 0:
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
        except OperationalError:
            # DB not ready during migrate
            pass
