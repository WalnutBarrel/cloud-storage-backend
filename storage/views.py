from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader
from .models import File

@api_view(["POST"])
def upload_file(request):
    uploaded_file = request.FILES.get("file")
    name = request.data.get("name")

    if not uploaded_file:
        return Response({"error": "No file"}, status=400)

    result = cloudinary.uploader.upload(uploaded_file)

    file = File.objects.create(
        name=name or uploaded_file.name,
        file_url=result["secure_url"],
        resource_type=result["resource_type"],
    )

    return Response({
        "id": file.id,
        "name": file.name,
        "file": file.file_url,
        "type": file.resource_type,
        "uploaded_at": file.uploaded_at,
    })


@api_view(["GET"])
def list_files(request):
    files = File.objects.all().order_by("-uploaded_at")
    return Response([
        {
            "id": f.id,
            "name": f.name,
            "file": f.file_url,
            "type": f.resource_type,
            "uploaded_at": f.uploaded_at,
        } for f in files
    ])


@api_view(["DELETE"])
def delete_file(request, file_id):
    file = File.objects.get(id=file_id)

    public_id = file.file_url.split("/")[-1].split(".")[0]
    cloudinary.uploader.destroy(public_id, resource_type=file.resource_type)

    file.delete()
    return Response({"success": True})


@api_view(["PUT"])
def rename_file(request, file_id):
    file = File.objects.get(id=file_id)
    file.name = request.data.get("name")
    file.save()
    return Response({"success": True})
