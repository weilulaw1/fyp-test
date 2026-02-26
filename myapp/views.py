import json
import os
import traceback
import sys
import subprocess
import zipfile
import shutil
from django.conf import settings
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
from pathlib import Path
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
    media_dir = Path(settings.MEDIA_ROOT)  # 🔹 directly MEDIA_ROOT

    if not media_dir.exists():
        return JsonResponse({"files": []})
        
    files = [
        str(p.relative_to(media_dir)).replace("\\", "/")
        for p in media_dir.rglob("*")
        if p.is_file()
    ]

    return JsonResponse({"files": files})


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
    


@csrf_exempt
def run_json_to_uml(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("json_file")
        if not uploaded_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded_file.name)

        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        script_dir = os.path.join(os.path.dirname(__file__), "..", "files")
        script_path = os.path.join(script_dir, "json_to_uml.py")

        output_dir = os.path.join(script_dir, "uml_output")
        os.makedirs(output_dir, exist_ok=True)

        try:
            result = subprocess.run(
                [sys.executable, script_path, file_path, output_dir],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

        except subprocess.CalledProcessError as e:
            print("UML generation failed!")
            print("STDERR:\n", e.stderr)
            traceback.print_exc()
            return JsonResponse({
                "error": "UML generation failed",
                "details": e.stderr,
            }, status=500)

        return JsonResponse({
            "status": "UML generated successfully",
            "uploaded_file": uploaded_file.name,
            "output_dir": output_dir,
        })
    print("OUTPUT DIR:", os.path.abspath(output_dir))

    return JsonResponse({"error": "Invalid request method"}, status=405)


@api_view(["POST"])
def archrec_upload_to_projects(request):
    """
    Receives folder upload (files + file_paths) and writes into:
      <files/arch rec demo>/data/projects/<project_name>/...

    Clears the target project folder each upload (so it's always fresh).
    """
    files = request.FILES.getlist("files")
    if not files:
        return JsonResponse({"error": "No files uploaded."}, status=400)

    file_paths_raw = request.POST.get("file_paths")
    try:
        file_paths = json.loads(file_paths_raw) if file_paths_raw else []
    except Exception:
        file_paths = []

    # path to: projct/test/files/arch rec demo
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files", "arch rec demo"))
    projects_root = os.path.join(base_dir, "data", "projects")
    os.makedirs(projects_root, exist_ok=True)

    # Decide project_name: use first path segment if present, else "current"
    # Example webkitRelativePath: "myrepo/src/main.py" -> project_name = "myrepo"
    first_rel = file_paths[0] if file_paths else files[0].name
    first_rel = first_rel.replace("\\", "/")
    project_name = first_rel.split("/")[0] if "/" in first_rel else "current"

    project_dir = os.path.join(projects_root, project_name)

    # Clear previous upload for this project
    if os.path.isdir(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir, exist_ok=True)

    saved = 0
    skipped = 0

    deny_parts = {"node_modules", "__pycache__", ".venv", ".git", "dist", "build"}

    for i, f in enumerate(files):
        rel = file_paths[i] if i < len(file_paths) else f.name
        rel = rel.replace("\\", "/")

        if rel.endswith(".DS_Store"):
            skipped += 1
            continue

        # filter junk
        parts = [p for p in rel.split("/") if p]
        if any(p in deny_parts for p in parts):
            skipped += 1
            continue

        # remove the top folder name from the stored path so we don't nest twice
        # store "src/a.py" instead of "myrepo/src/a.py"
        if len(parts) >= 2 and parts[0] == project_name:
            rel_inside = "/".join(parts[1:])
        else:
            rel_inside = "/".join(parts)

        # safe normalize
        rel_inside = os.path.normpath(rel_inside).lstrip("\\/")

        out_path = os.path.join(project_dir, rel_inside)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "wb") as dst:
            for chunk in f.chunks():
                dst.write(chunk)

        saved += 1

    return JsonResponse({
        "status": "uploaded",
        "project_name": project_name,
        "project_dir": project_dir,
        "files_saved": saved,
        "files_skipped": skipped,
    })

@csrf_exempt
def archrec_run_summarize(request):
    """
    CHAINED:
      1) Run summarize_projects.py
      2) Find latest summary JSON
      3) Run json_to_uml.py using that JSON
      4) Copy summary + uml output into MEDIA_ROOT so frontend FolderView can see it
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files", "arch rec demo"))
    summarize_script = os.path.join(base_dir, "summarize_projects.py")

    # 1) Run summarizer
    try:
        res = subprocess.run(
            [sys.executable, summarize_script],
            cwd=base_dir,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as e:
        traceback.print_exc()
        return JsonResponse({
            "error": "Summarization failed",
            "returncode": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr,
        }, status=500)

    project_name = _pick_project_name(base_dir)
    summaries_dir = os.path.join(base_dir, "data", "summaries")

    # 2) Pick summary JSON
    summary_json = _find_latest_summary_json(summaries_dir, project_name)
    if not summary_json:
        return JsonResponse({
            "error": "No summary JSON found after summarization",
            "summaries_dir": summaries_dir,
            "stdout": res.stdout,
        }, status=500)

    # 3) Run json_to_uml into a temp/output folder under arch rec demo
    uml_local_out = os.path.join(base_dir, "uml_output", project_name)
    try:
        # clean old uml for this project
        if os.path.isdir(uml_local_out):
            shutil.rmtree(uml_local_out)
        uml_run = _run_json_to_uml_local(base_dir, summary_json, uml_local_out)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            "error": "UML generation failed",
            "details": str(e),
            "summary_json": summary_json,
        }, status=500)

    # 4) "Auto upload folder" = copy artifacts into MEDIA_ROOT
    # so FolderView (which lists MEDIA_ROOT) can show them.
    media_summaries_dir = os.path.join(settings.MEDIA_ROOT, "archrec", "summaries", project_name)
    media_uml_dir = os.path.join(settings.MEDIA_ROOT, "uml_output", project_name)

    try:
        os.makedirs(media_summaries_dir, exist_ok=True)

        # copy summary json
        shutil.copy2(summary_json, os.path.join(media_summaries_dir, os.path.basename(summary_json)))

        # replace UML folder
        if os.path.isdir(media_uml_dir):
            shutil.rmtree(media_uml_dir)
        shutil.copytree(uml_local_out, media_uml_dir)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            "error": "Failed to copy outputs into MEDIA_ROOT",
            "details": str(e),
            "media_uml_dir": media_uml_dir,
            "media_summaries_dir": media_summaries_dir,
        }, status=500)

    return JsonResponse({
        "status": "pipeline completed",
        "project_name": project_name,
        "summary_json": summary_json,
        "media_summary_dir": media_summaries_dir.replace("\\", "/"),
        "media_uml_dir": media_uml_dir.replace("\\", "/"),
        "summarize_stdout": res.stdout,
        "uml_stdout": uml_run.get("stdout", ""),
    })



def _pick_project_name(base_dir: str) -> str:
    projects_root = os.path.join(base_dir, "data", "projects")
    if not os.path.isdir(projects_root):
        return "current"

    # Prefer: if exactly one project folder exists, use it
    candidates = [
        d for d in os.listdir(projects_root)
        if os.path.isdir(os.path.join(projects_root, d))
    ]
    if len(candidates) == 1:
        return candidates[0]

    # Fallback: newest modified project folder
    if candidates:
        candidates.sort(
            key=lambda d: os.path.getmtime(os.path.join(projects_root, d)),
            reverse=True
        )
        return candidates[0]

    return "current"


def _find_latest_summary_json(summaries_dir: str, project_name: str) -> str | None:
    """
    Tries to find the most relevant JSON produced by summarize_projects.py.
    Prefers files that contain project_name in filename, else newest json.
    """
    if not os.path.isdir(summaries_dir):
        return None

    all_json = []
    for root, _, files in os.walk(summaries_dir):
        for f in files:
            if f.lower().endswith(".json"):
                p = os.path.join(root, f)
                all_json.append(p)

    if not all_json:
        return None

    # Prefer name match
    matched = [p for p in all_json if project_name.lower() in os.path.basename(p).lower()]
    target_list = matched if matched else all_json

    target_list.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return target_list[0]


def _run_json_to_uml_local(base_dir: str, json_path: str, out_dir: str) -> dict:
    """
    Finds and runs json_to_uml.py somewhere under base_dir.
    """
    script_path = _find_file_recursive(base_dir, "json_to_uml.py")
    if not script_path:
        raise FileNotFoundError(f"json_to_uml.py not found under: {base_dir}")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"summary json not found at: {json_path}")

    os.makedirs(out_dir, exist_ok=True)

    res = subprocess.run(
        [sys.executable, script_path, json_path, out_dir],
        cwd=os.path.dirname(script_path),     # safer for relative imports
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {"stdout": res.stdout, "stderr": res.stderr, "script_path": script_path}


def _find_file_recursive(root_dir: str, filename: str) -> str | None:
    for root, _, files in os.walk(root_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

