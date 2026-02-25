from pathlib import Path
import requests
import time
import sys
import os
# from label_studio_sdk import Client
from label_studio_sdk import LabelStudio

from core.models import Image, ImageGame, Game
from lib.helpers import setup_logger, get_config
from .lib_images import get_images_ondisk, image_sort

logger = setup_logger()
config = get_config()

# from label_studio_sdk.client import LabelStudio
from label_studio_sdk.core.api_error import ApiError


LABEL_STUDIO_TOKEN = os.getenv("LABEL_STUDIO_TOKEN")

if not LABEL_STUDIO_TOKEN:
    logger.error("LABEL_STUDIO_TOKEN environment variable is not set.")
    raise ValueError("LABEL_STUDIO_TOKEN environment variable is not set.")


def image_ls_list_projects_action(request):
    logger.info(
        "This is the main function for the labelstudio image processing module."
    )
    # get the list of projects from labelstudio
    ls = LabelStudio(
        base_url=config["api"]["labels_url"], api_key=LABEL_STUDIO_TOKEN, timeout=10
    )

    projects = list(ls.projects.list())
    project_list = [{"id": p.id, "title": p.title} for p in projects]
    logger.info(f"Retrieved {project_list} projects from labelstudio.")
    return project_list


def image_ls_projfile_action(project_id, max_tasks=None):
    # gets the list of images in the project and returns it as a json file
    logger.info(
        "This is the main function for the labelstudio image processing module."
    )

    if not project_id:
        logger.error("Project ID is required.")
        raise ValueError("Project ID is required.")

    # get the project file from labelstudio
    ls = LabelStudio(
        base_url=config["api"]["labels_url"], api_key=LABEL_STUDIO_TOKEN, timeout=60
    )
    pager = ls.tasks.list(project=project_id)  # <-- keep as pager/iterator
    tasks = []
    for i, t in enumerate(pager, start=1):
        tasks.append(
            {
                "id": t.id,
                "data": t.data,
            }
        )
        if max_tasks and i >= max_tasks:
            break
    logger.info(f"Retrieved {tasks} tasks from labelstudio project {project_id}.")
    logger.info(f"Exported project {project_id} from labelstudio.")

    return tasks


def send_labelstudio(project_id):
    logger.info("Sending images to Label Studio project %s", project_id)
    ls = LabelStudio(
        base_url=config["api"]["labels_url"], api_key=LABEL_STUDIO_TOKEN, timeout=60
    )
    try:
        # ++ look up storage ID for this project instead of hardcoding ++
        storages = list(ls.import_storage.local.list(project=project_id))
        if not storages:
            raise RuntimeError(f"No local storage configured for project {project_id}")
        storage_id = storages[0].id
        logger.info("Found storage ID %s for project %s", storage_id, project_id)
        return ls.import_storage.local.sync(id=storage_id)
    except RuntimeError:
        raise
    except Exception as exc:
        logger.exception("Error sending images to Label Studio")
        raise RuntimeError(f"Error sending images to Label Studio: {exc}") from exc


def export_and_download_snapshot(project_id):
    """Export project JSON snapshot

    This example demonstrates how to:
    - Create an export snapshot
    - Poll for completion
    - Download the resulting file
    """
    # base_url = os.getenv("LABEL_STUDIO_URL")
    # api_key = os.getenv("LABEL_STUDIO_API_KEY")
    project_id_str = str(project_id)
    base_url = config["api"]["labels_url"]
    api_key = LABEL_STUDIO_TOKEN
    timeout = 60
    if not base_url or not api_key or not project_id_str:
        logger.error(
            "set LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY and LABEL_STUDIO_PROJECT_ID env vars"
        )
        sys.exit(1)

    try:
        project_id = int(project_id_str)
    except ValueError:
        logger.error("LABEL_STUDIO_PROJECT_ID must be an integer")
        sys.exit(1)

    # Initialize v2 client
    ls = LabelStudio(base_url=base_url, api_key=api_key)

    # Fetch project and optional first view id
    ls.projects.get(id=project_id)
    views = ls.views.list(project=project_id)
    {"view": views[0].id} if views else None

    # Create export snapshot
    create_kwargs = {
        "title": "Export SDK Snapshot",
        # task_filter_options follows API schema; pass only if a view is available
        # "task_filter_options": {"view": task_filter_options["view"]} if task_filter_options else None,
    }
    # Remove None keys to avoid sending them
    create_kwargs = {k: v for k, v in create_kwargs.items() if v is not None}

    export_job = ls.projects.exports.create(id=project_id, **create_kwargs)
    export_id = export_job.id
    logger.info(f"Created export snapshot: id={export_id}, status={export_job.status}")

    # Poll until completed or failed
    start = time.time()
    timeout_sec = 300
    logger.info("Waiting for export snapshot to complete...")
    while True:
        job = ls.projects.exports.get(id=project_id, export_pk=export_id)
        elapsed = int(time.time() - start)
        logger.info(f"Export status: {job.status} (elapsed {elapsed}s)")
        if job.status in ("completed", "failed"):
            break
        if time.time() - start > timeout_sec:
            raise TimeoutError(
                f"Export job timed out (id={export_id}, status={job.status})"
            )
        time.sleep(1.0)

    if job.status == "failed":
        raise ApiError(status_code=500, body=f"Export failed: {job}")

    # Download export as JSON to local file
    out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"project_{project_id}_export_{export_id}.json"

    with open(out_path, "wb") as f:
        for chunk in ls.projects.exports.download(
            id=project_id,
            export_pk=export_id,
            export_type="JSON",
            request_options={"chunk_size": 1024},
        ):
            f.write(chunk)

    logger.info(f"Export completed. File saved to: {out_path}")
    return export_id


def convert_snapshot(project_id, outdir, export_type: str, export_id: str = None):
    """Convert the project export JSON snapshot to a specified format and download it.

    The conversion API is used to start a conversion on the Label Studio backend, then we poll export status
    until the specific converted format is completed, and finally download it.
    See docs: projects/exports/convert and projects/exports/list.

    Args:
        project_id: The ID of the project.
        export_id: The ID of the export to convert. If not provided, the latest export will be used.
    """
    project_id_str = str(project_id)
    base_url = config["api"]["labels_url"]
    api_key = LABEL_STUDIO_TOKEN
    if not base_url or not api_key or not project_id_str:
        logger.error(
            "set LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY and LABEL_STUDIO_PROJECT_ID env vars"
        )
        sys.exit(1)

    try:
        project_id = int(project_id_str)
    except ValueError:
        logger.error("LABEL_STUDIO_PROJECT_ID must be an integer")
        sys.exit(1)

    ls = LabelStudio(base_url=base_url, api_key=api_key)

    # Get the latest export snapshot for the project
    exports = ls.projects.exports.list(id=project_id)
    if not exports:
        raise ApiError(
            status_code=404, body="No export snapshots found for the project"
        )
    exports = sorted(exports, key=lambda e: e.created_at, reverse=True)
    export = exports[0]
    export_id = export.id if not export_id else export_id

    # Start conversion
    conv = ls.projects.exports.convert(
        export_pk=export_id, id=project_id, export_type=export_type
    )
    converted_format_id = conv.converted_format
    logger.info(
        f"Started conversion: export_id={export_id}, export_type={export_type}, converted_format_id={converted_format_id}"
    )

    # Poll converted format status
    start = time.time()
    timeout_sec = 300
    logger.info("Waiting for conversion to complete...")
    while True:
        cur = ls.projects.exports.get(id=project_id, export_pk=export_id)
        cf = None
        if cur.converted_formats:
            cf = next(
                (
                    c
                    for c in cur.converted_formats
                    if (converted_format_id and c.id == converted_format_id)
                    or (c.export_type == export_type)
                ),
                None,
            )
        status = getattr(cf, "status", None)
        elapsed = int(time.time() - start)
        logger.info(
            f"Conversion status: {status or 'pending'} (format {export_type}, elapsed {elapsed}s)"
        )
        if status in ("completed", "failed"):
            break
        if time.time() - start > timeout_sec:
            raise TimeoutError(
                f"Conversion timed out (export_id={export_id}, format={export_type}, status={status})"
            )
        time.sleep(1.0)

    if status == "failed":
        raise ApiError(
            status_code=500,
            body=f"Conversion failed (export_id={export_id}, format={export_type})",
        )

    # Download converted file using export_type param
    ext = "json" if export_type.upper().startswith("JSON") else export_type.lower()
    out_dir = Path(outdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"project_{project_id}_export_{export_id}.{ext}"

    with open(out_path, "wb") as f:
        for chunk in ls.projects.exports.download(
            id=project_id,
            export_pk=export_id,
            export_type=export_type,
            request_options={"chunk_size": 1024},
        ):
            f.write(chunk)

    logger.info(f"Converted export downloaded. File saved to: {out_path}")


# if __name__ == "__main__":
#
#    export_id = export_and_download_snapshot()
#    logger.info(f"Export ID: {export_id}")#
#
#    export_type = os.getenv("LABEL_STUDIO_EXPORT_TYPE", None)
#    if export_type and export_type != "JSON":
#        logger.info(f"Converting export to {export_type} format")
#        convert_snapshot(export_type, export_id)
