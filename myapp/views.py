import os
import zipfile
from django.conf import settings
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging

@api_view(['GET'])
def home_data(request):
    return Response({"message": "Hello from Django backend 🚀"})

@api_view(['GET'])
def file_new(request):
    return Response({"message":"New File Created"})

@api_view(['GET'])
def file_open(request):
    return Response({"message": "Opened file"})

@api_view(['GET'])
def file_save(request):
    return Response({"message": "File saved"})

@api_view(['GET'])
def edit_undo(request):
    return Response({"message": "Undo action"})

@api_view(['GET'])
def edit_redo(request):
    return Response({"message": "Redo action"})

@api_view(['GET'])
def toggle_sidebar(request):
    return Response({"message": "Sidebar toggled"})

def unpack_zip(file):
    folder_name = os.path.splitext(file.name)[0]
    folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    with zipfile.ZipFile(file) as zip_ref:
        for name in zip_ref.namelist():
            if name.endswith('/'):
                continue
            file_data = zip_ref.read(name)
            file_path = os.path.join(folder_path, name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f_out:
                f_out.write(file_data)
    return folder_path

logger = logging.getLogger('myapp')

@csrf_exempt
def upload_file(request):
    if request.method != 'POST':
        return JsonResponse({"message": "Invalid request method"}, status=405)

    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({"message": "No files uploaded."}, status=400)

    saved_files = []

    for f in files:
        logger.info(f"Received zip file: {f.name}")
        if f.name.endswith('.zip'):
            folder_path = unpack_zip(f)
            logger.info(f"Unpacked zip to: {folder_path}")
            saved_files.append(f"{f.name} (unzipped to {folder_path})")
        else:
            default_storage.save(f.name, ContentFile(f.read()))
            saved_files.append(f.name)
            logger.info(f"Saved file to MEDIA_ROOT: {f.name}")

    return JsonResponse({
        "message": f"{len(saved_files)} files uploaded successfully!",
        "files": saved_files
    })