from django.urls import path
from .views import upload_file, list_files, delete_file, rename_file

urlpatterns = [
    path("upload/", upload_file),
    path("files/", list_files),
    path("files/<int:file_id>/", delete_file),
    path("files/<int:file_id>/rename/", rename_file),
]
