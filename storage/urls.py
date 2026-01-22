from django.urls import path
from .views import upload_file, list_files, delete_file, rename_file, list_folders, create_folder
from .views import download_zip, storage_stats, health_check, clear_all_files, download_all_media, list_image_urls
from .views import download_file, create_cloudinary_zip

urlpatterns = [
    path("upload/", upload_file),
    path("files/", list_files),
    path("files/<int:file_id>/", delete_file),
    path("files/<int:file_id>/rename/", rename_file),
    #folders
    path("folders/", list_folders),
    path("folders/create/", create_folder),
    path("files/download-zip/", download_zip),
    path("storage/stats/", storage_stats),
    path("health/", health_check),
    path("files/clear/", clear_all_files),
    path("files/download-all-images/", download_all_media),
    path("files/list-image-urls/", list_image_urls),
    path("files/<int:file_id>/download/", download_file),
    path("files/create-cloudinary-zip/", create_cloudinary_zip),

]
