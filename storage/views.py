from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader

from .models import File, Folder


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

    result = cloudinary.uploader.upload(uploaded_file)

    file = File.objects.create(
        name=name or uploaded_file.name,
        file_url=result["secure_url"],
        resource_type=result["resource_type"],
        folder=folder,
    )

    return Response({
        "id": file.id,
        "name": file.name,
        "file": file.file_url,
        "type": file.resource_type,
        "folder": file.folder.id if file.folder else None,
        "uploaded_at": file.uploaded_at,
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
        }
        for f in files.order_by("-uploaded_at")
    ])


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
