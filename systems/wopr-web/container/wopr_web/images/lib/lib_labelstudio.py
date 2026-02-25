import requests
import os
# from label_studio_sdk import Client
from label_studio_sdk import LabelStudio

from core.models import Image, ImageGame, Game
from lib.helpers import setup_logger, get_config
from .lib_images import get_images_ondisk, image_sort

logger = setup_logger()
config = get_config()

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
    logger.info("Starting send_labelstudio function")
    logger.info(f"Sending images to Label Studio project {project_id}")
    ls = LabelStudio(
        base_url=config["api"]["labels_url"], api_key=LABEL_STUDIO_TOKEN, timeout=60
    )
    try:
        res = ls.storages.localfiles.sync(id=1, project_id=project_id)
    except Exception as exc:
        logger.exception("Error sending images to Label Studio")
        raise RuntimeError(f"Error sending images to Label Studio: {exc}")
    return res
