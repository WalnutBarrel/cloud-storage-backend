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
        return Response({"error": "No file provided"}, status=400)

    # Upload to Cloudinary
    result = cloudinary.uploader.upload(uploaded_file)

    # Save URL in DB
    file = File.objects.create(
        name=name or uploaded_file.name,
        file_url=result["secure_url"],
    )

    return Response(
        {
            "id": file.id,
            "name": file.name,
            "file": file.file_url,
            "uploaded_at": file.uploaded_at,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def list_files(request):
    files = File.objects.all().order_by("-uploaded_at")

    data = [
        {
            "id": f.id,
            "name": f.name,
            "file": f.file_url,
            "uploaded_at": f.uploaded_at,
        }
        for f in files
    ]

    return Response(data)
