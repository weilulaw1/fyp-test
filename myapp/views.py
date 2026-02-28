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

    root_key = request.GET.get("root","media")

    media_root = Path(settings.MEDIA_ROOT).resolve()  # 🔹 directly MEDIA_ROOT

    archrec_projects_root = Path(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files", "arch rec demo", "data", "projects"))
    ).resolve()

    ROOTS = {
        "media": media_root,
        "projects" : archrec_projects_root,
    }
    base_dir = ROOTS.get(root_key, media_root)

    if not base_dir.exists():
        return JsonResponse({"files": [], "root": root_key})

    files = [
        str(p.relative_to(base_dir)).replace("\\", "/")
        for p in base_dir.rglob("*")
        if p.is_file()
    ]
    return JsonResponse({"files": files, "root": root_key})


@api_view(['GET'])
def get_uml_file(request, filename):
    file_path = os.path.join("media", filename)  # adjust path
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return HttpResponse(f.read(), content_type="text/plain")
    return HttpResponse("File not found", status=404)


@api_view(['GET'])
def file_detail(request, filename):

    filename = unquote(filename).rstrip('/')

    root_key = request.GET.get("root", "media")

    media_root = Path(settings.MEDIA_ROOT).resolve()
    archrec_projects_root = Path(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files", "arch rec demo", "data", "projects"))
    ).resolve()

    ROOTS = {
        "media": media_root,
        "projects": archrec_projects_root,
    }

    base_dir = ROOTS.get(root_key, media_root)

    # Build + normalize + secure check
    safe_path = (base_dir / filename).resolve()
    if base_dir not in safe_path.parents and safe_path != base_dir:
        return HttpResponse("Forbidden", status=403)

    if safe_path.exists() and safe_path.is_file():
        with open(safe_path, "r", encoding="utf-8", errors="ignore") as f:
            return HttpResponse(f.read(), content_type="text/plain")

    return HttpResponse("File not found", status=404)


@csrf_exempt  # remove if you handle CSRF token in frontend
@require_POST
def delete_file(request):
    rel = request.POST.get("path")
    root_key = request.POST.get("root", "media")
    if not rel:
        return JsonResponse({"error": "No path provided"}, status=400)

    media_root = Path(settings.MEDIA_ROOT).resolve()
    archrec_projects_root = Path(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files", "arch rec demo", "data", "projects"))
    ).resolve()

    ROOTS = {
        "media": media_root,
        "projects": archrec_projects_root,
    }

    base_dir = ROOTS.get(root_key, media_root)

    target = (base_dir / rel).resolve()
    if base_dir not in target.parents and target != base_dir:
        return JsonResponse({"error": "Forbidden"}, status=403)

    if not target.exists():
        return JsonResponse({"error": "File does not exist"}, status=404)

    try:
        if target.is_file():
            target.unlink()
        else:
            shutil.rmtree(str(target))
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def run_json_to_uml(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

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

    json_stem = os.path.splitext(uploaded_file.name)[0]
    output_dir = os.path.join(settings.MEDIA_ROOT, "uml_output", json_stem)

    temp_dir = output_dir + "_tmp"

    # 1) fresh temp dir
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    # 2) run script INTO temp dir
    try:
        result = subprocess.run(
            [sys.executable, script_path, file_path, temp_dir],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as e:
        traceback.print_exc()
        # cleanup temp, keep old output_dir
        try:
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            pass
        return JsonResponse({
            "error": "UML generation failed",
            "details": e.stderr,
        }, status=500)

    # 3) swap in new outputs ONLY after success
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    os.rename(temp_dir, output_dir)

    return JsonResponse({
        "status": "UML generated successfully",
        "uploaded_file": uploaded_file.name,
        "media_uml_dir": output_dir.replace("\\", "/"),
        "stdout": result.stdout,
    })

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
    if request.method != "POST":
        return _json_error("Invalid request method", status=405)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files", "arch rec demo"))
    summarize_script = os.path.join(base_dir, "summarize_projects.py")

    if not os.path.exists(summarize_script):
        return _json_error("summarize_projects.py not found", status=500, summarize_script=summarize_script)

    # 1) Run summarizer ONCE
    try:
        res = subprocess.run(
            [sys.executable, summarize_script],
            cwd=base_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        logger.info("summarize stdout:\n%s", res.stdout)
        logger.info("summarize stderr:\n%s", res.stderr)
    except subprocess.CalledProcessError as e:
        logger.error("Summarize failed. returncode=%s", e.returncode)
        logger.error("STDOUT:\n%s", e.stdout)
        logger.error("STDERR:\n%s", e.stderr)
        return _json_error(
            "Summarization failed",
            status=500,
            returncode=e.returncode,
            stdout=e.stdout,
            stderr=e.stderr,
        )
    except Exception as e:
        logger.exception("Unexpected error while running summarizer")
        return _json_error("Unexpected error while running summarizer", status=500, details=str(e))

    # 2) Pick project + summary JSON
    project_name = _pick_project_name(base_dir)
    summaries_dir = os.path.join(base_dir, "data", "summaries")

    summary_json = _find_latest_summary_json(summaries_dir, project_name)
    if not summary_json:
        return _json_error(
            "No summary JSON found after summarization",
            status=500,
            summaries_dir=summaries_dir,
            stdout=res.stdout,
            stderr=res.stderr,
        )

    # 3) Run json_to_uml into local out folder under arch rec demo
    uml_local_out = os.path.join(base_dir, "uml_output", project_name)
    try:
        if os.path.isdir(uml_local_out):
            shutil.rmtree(uml_local_out)
        uml_run = _run_json_to_uml_local(base_dir, summary_json, uml_local_out)
    except Exception as e:
        logger.exception("UML generation failed")
        return _json_error(
            "UML generation failed",
            status=500,
            details=str(e),
            summary_json=summary_json,
        )

    # 4) Copy outputs into MEDIA_ROOT
    media_summaries_dir = os.path.join(settings.MEDIA_ROOT, "archrec", "summaries", project_name)
    media_uml_dir = os.path.join(settings.MEDIA_ROOT, "uml_output", project_name)

    try:
        os.makedirs(media_summaries_dir, exist_ok=True)
        shutil.copy2(summary_json, os.path.join(media_summaries_dir, os.path.basename(summary_json)))

        if os.path.isdir(media_uml_dir):
            shutil.rmtree(media_uml_dir)
        shutil.copytree(uml_local_out, media_uml_dir)
    except Exception as e:
        logger.exception("Failed to copy outputs into MEDIA_ROOT")
        return _json_error(
            "Failed to copy outputs into MEDIA_ROOT",
            status=500,
            details=str(e),
            media_uml_dir=media_uml_dir,
            media_summaries_dir=media_summaries_dir,
        )

    return JsonResponse({
        "status": "pipeline completed",
        "project_name": project_name,
        "summary_json": summary_json,
        "media_summary_dir": media_summaries_dir.replace("\\", "/"),
        "media_uml_dir": media_uml_dir.replace("\\", "/"),
        "summarize_stdout": res.stdout,
        "summarize_stderr": res.stderr,  # IMPORTANT: logs usually go here
        "uml_stdout": uml_run.get("stdout", ""),
        "uml_stderr": uml_run.get("stderr", ""),
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
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files", "json_to_uml.py"))
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"json_to_uml.py not found at: {script_path}")
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

def _json_error(message: str, *, status=500, **extra):
    # Prevent huge responses; keep frontend responsive
    def _clip(s, n=8000):
        if s is None:
            return ""
        s = str(s)
        return s if len(s) <= n else (s[:n] + "\n...[truncated]...")

    payload = {"error": message}
    for k, v in extra.items():
        if k in ("stdout", "stderr", "details", "traceback"):
            payload[k] = _clip(v)
        else:
            payload[k] = v
    return JsonResponse(payload, status=status)
