from django.db import models

class Folder(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StorageAccount(models.Model):
    name = models.CharField(max_length=50)
    cloud_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100)
    api_secret = models.CharField(max_length=100)
    used_bytes = models.BigIntegerField(default=0)
    limit_bytes = models.BigIntegerField(default=24 * 1024 * 1024 * 1024)


class File(models.Model):
    name = models.CharField(max_length=255)
    file_url = models.URLField()
    resource_type = models.CharField(max_length=20)
    folder = models.ForeignKey(
        Folder,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="files"
    )
    size = models.BigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    storage_account = models.ForeignKey(StorageAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


