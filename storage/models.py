from django.db import models

class File(models.Model):
    name = models.CharField(max_length=255)
    file_url = models.URLField()
    resource_type = models.CharField(max_length=20)  # image, video, raw
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
