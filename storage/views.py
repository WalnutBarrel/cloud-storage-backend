from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader
from .models import File, Folder, StorageAccount
import zipfile
import io
import requests
from django.http import HttpResponse
from .models import pick_storage_account
import cloudinary
import zipfile
import tempfile
import os
import requests
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response




# =====================
# FILE APIs
# =====================

@api_view(["POST"])
def upload_file(request):
    uploaded_file = request.FILES.get("file")
    name = request.data.get("name")
    folder_id = request.data.get("folder")

    if not uploaded_file:
        return Response({"error": "No file"}, status=400)

    folder = None
    if folder_id:
        folder = Folder.objects.get(id=folder_id)

    # ✅ NEW: pick account using file size
    try:
        account = pick_storage_account(uploaded_file.size)
    except Exception:
        return Response(
            {"error": "All storage accounts are full"},
            status=507
        )

    # configure correct Cloudinary account
    cloudinary.config(
        cloud_name=account.cloud_name,
        api_key=account.api_key,
        api_secret=account.api_secret,
        secure=True,
    )

    result = cloudinary.uploader.upload(
    uploaded_file,
    resource_type="auto",
    chunk_size=6_000_000  # allows large videos
)


    file = File.objects.create(
        name=name or uploaded_file.name,
        file_url=result["secure_url"],
        resource_type=result["resource_type"],
        folder=folder,
        size=result.get("bytes", 0),
        storage_account=account,
    )

    # update usage
    account.used_bytes += result.get("bytes", 0)
    account.save()

    return Response({
        "id": file.id,
        "name": file.name,
        "file": file.file_url,
        "folder": file.folder.id if file.folder else None,
    })




@api_view(["GET"])
def list_files(request):
    folder_id = request.GET.get("folder")

    if folder_id:
        files = File.objects.filter(folder_id=folder_id)
    else:
        files = File.objects.filter(folder__isnull=True)

    return Response([
    {
        "id": f.id,
        "name": f.name,
        "file": f.file_url,
        "type": f.resource_type,
        "folder": f.folder.id if f.folder else None,
        "uploaded_at": f.uploaded_at,
        "size": f.size,

        # 🔥 NEW
        "storage_account": {
            "id": f.storage_account.id,
            "name": f.storage_account.name,
        }
    }
    for f in files.order_by("-uploaded_at")
])




@api_view(["DELETE"])
def delete_file(request, file_id):
    file = File.objects.get(id=file_id)
    account = file.storage_account

    # ✅ configure the SAME account used for upload
    cloudinary.config(
        cloud_name=account.cloud_name,
        api_key=account.api_key,
        api_secret=account.api_secret,
        secure=True,
    )

    public_id = file.file_url.split("/")[-1].split(".")[0]
    cloudinary.uploader.destroy(
        public_id,
        resource_type=file.resource_type
    )

    # ✅ free storage
    account.used_bytes -= file.size
    if account.used_bytes < 0:
        account.used_bytes = 0
    account.save()

    file.delete()
    return Response({"success": True})



@api_view(["PUT"])
def rename_file(request, file_id):
    file = File.objects.get(id=file_id)
    file.name = request.data.get("name")
    file.save()
    return Response({"success": True})



# =====================
# FOLDER APIs
# =====================

@api_view(["POST"])
def create_folder(request):
    name = request.data.get("name")

    if not name:
        return Response({"error": "Folder name required"}, status=400)

    folder = Folder.objects.create(name=name)
    return Response({
        "id": folder.id,
        "name": folder.name,
        "created_at": folder.created_at,
    })


@api_view(["GET"])
def list_folders(request):
    folders = Folder.objects.all().order_by("name")
    return Response([
        {
            "id": f.id,
            "name": f.name,
            "created_at": f.created_at,
        }
        for f in folders
    ])


@api_view(["POST"])
def download_zip(request):
    file_ids = request.data.get("files", [])

    if not file_ids:
        return Response({"error": "No files selected"}, status=400)

    files = File.objects.filter(id__in=file_ids)

    if not files.exists():
        return Response({"error": "Files not found"}, status=404)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for f in files:
            r = requests.get(f.file_url, timeout=15)
            if r.status_code == 200:
                zip_file.writestr(f.name, r.content)

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="files.zip"'
    return response



@api_view(["GET"])
def storage_stats(request):
    accounts = StorageAccount.objects.all().order_by("id")

    return Response([
        {
            "id": a.id,
            "name": a.name,
            "used_gb": round(a.used_bytes / (1024**3), 2),
            "limit_gb": round(a.limit_bytes / (1024**3), 2),
            "free_gb": round((a.limit_bytes - a.used_bytes) / (1024**3), 2),
            "percent_used": round((a.used_bytes / a.limit_bytes) * 100, 2),
        }
        for a in accounts
    ])


from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(["GET", "HEAD"])
def health_check(request):
    return JsonResponse({"status": "ok"})


@api_view(["DELETE"])
def clear_all_files(request):
    File.objects.all().delete()
    return Response({"success": True})


@api_view(["GET"])
def download_all_media(request):
    files = File.objects.filter(resource_type__in=["image", "video"])

    if not files.exists():
        return Response({"error": "No media found"}, status=404)

    # Create temp zip file on disk (NOT memory)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    zip_path = tmp.name
    tmp.close()

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in files:
                r = requests.get(f.file_url, stream=True, timeout=30)
                if r.status_code == 200:
                    zipf.writestr(f.name, r.content)

        return FileResponse(
            open(zip_path, "rb"),
            as_attachment=True,
            filename="all_media.zip",
        )

    finally:
        # cleanup after response is sent
        try:
            os.unlink(zip_path)
        except Exception:
            pass


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import File

@api_view(["GET"])
def list_image_urls(request):
    files = File.objects.filter(resource_type="image")

    return Response([
        {
            "name": f.name,
            "url": f.file_url,
        }
        for f in files
    ])


from django.http import StreamingHttpResponse
import requests
import os

@api_view(["GET"])
def download_file(request, file_id):
    file = File.objects.get(id=file_id)

    r = requests.get(file.file_url, stream=True, timeout=15)

    response = StreamingHttpResponse(
        r.iter_content(chunk_size=8192),
        content_type="application/octet-stream"
    )

    filename = file.name or os.path.basename(file.file_url)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response
