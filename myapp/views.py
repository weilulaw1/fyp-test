import json
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
from urllib.parse import unquote
from django.views.decorators.http import require_POST



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

    extracted_files = []
    with zipfile.ZipFile(file) as zip_ref:
        for name in zip_ref.namelist():
            if name.endswith('/'):
                continue
            file_data = zip_ref.read(name)
            file_path = os.path.join(folder_path, name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f_out:
                f_out.write(file_data)
            extracted_files.append(os.path.join(folder_name, name))
    return folder_path, extracted_files

logger = logging.getLogger('myapp')

@api_view(['POST'])
def upload_file(request):

    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({"message": "No files uploaded."}, status=400)

    # Get file paths from the frontend
    file_paths = request.POST.get("file_paths")
    if file_paths:
        try:
            file_paths = json.loads(file_paths)
        except Exception as e:
            file_paths = []
            logger.error(f"Failed to parse file_paths: {e}")
    else:
        file_paths = []

    saved_files = []

    for i, f in enumerate(files):
        # Use the relative path if provided, else fallback to file name
        relative_path = file_paths[i] if i < len(file_paths) else f.name
        logger.info(f"Received file: {f.name}, saving to: {relative_path}")

        if relative_path.endswith(".DS_Store"):
            continue

        # Create full path under MEDIA_ROOT
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        saved_files.append(relative_path)
        logger.info(f"Saved file to: {relative_path}")

    return JsonResponse({
        "message": f"{len(saved_files)} files uploaded successfully!",
        "files": saved_files
    })

@api_view(['GET'])
def list_files(request):
    media_dir = settings.MEDIA_ROOT  # 🔹 directly MEDIA_ROOT
    file_paths = []

    for root, dirs, files in os.walk(media_dir):
        for file in files:
            rel_dir = os.path.relpath(root, media_dir)
            rel_file = os.path.join(rel_dir, file) if rel_dir != "." else file
            file_paths.append(rel_file)

    return JsonResponse({"files": file_paths})


@api_view(['GET'])
def get_uml_file(request, filename):
    file_path = os.path.join("media", filename)  # adjust path
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return HttpResponse(f.read(), content_type="text/plain")
    return HttpResponse("File not found", status=404)

import logging
logger = logging.getLogger('myapp')

@api_view(['GET'])
def file_detail(request, filename):

    filename = unquote(filename).rstrip('/')
    
    # Convert URL path (forward slashes) into OS path
    safe_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, filename))
    
    # Security check: ensure the file is inside MEDIA_ROOT
    if not safe_path.startswith(os.path.abspath(settings.MEDIA_ROOT)):
        return HttpResponse("Forbidden", status=403)

    logger.info(f"Fetching file: {safe_path}")

    if os.path.exists(safe_path):
        with open(safe_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        logger.info(f"File length: {len(content)}")
        return HttpResponse(content, content_type="text/plain")
    
    logger.warning(f"File not found: {safe_path}")
    return HttpResponse("File not found", status=404)


@csrf_exempt  # remove if you handle CSRF token in frontend
@require_POST
def delete_file(request):
    path = request.POST.get("path")
    if not path:
        return JsonResponse({"error": "No path provided"}, status=400)

    # Make sure the path is safe and inside media folder
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(full_path):
        return JsonResponse({"error": "File does not exist"}, status=404)

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            import shutil
            shutil.rmtree(full_path)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)