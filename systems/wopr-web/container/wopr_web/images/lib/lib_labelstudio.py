import requests
import os
# from label_studio_sdk import Client
from label_studio_sdk import LabelStudio

from lib.helpers import setup_logger, get_config
from .lib_images import get_images_ondisk, image_sort

logger = setup_logger()
config = get_config()

LABEL_STUDIO_TOKEN = os.getenv("LABEL_STUDIO_TOKEN")

if not LABEL_STUDIO_TOKEN:
    logger.error("LABEL_STUDIO_TOKEN environment variable is not set.")
    raise ValueError("LABEL_STUDIO_TOKEN environment variable is not set.")


def image_ls_list_projects_action(request):
    logger.info("This is the main function for the labelstudio image processing module.")
    # get the list of projects from labelstudio
    ls = LabelStudio(base_url=config["api"]["labels_url"], api_key=LABEL_STUDIO_TOKEN, timeout=10)
    
    projects = list(ls.projects.list())
    project_list = [{"id": p.id, "title": p.title} for p in projects]
    logger.info(f"Retrieved {project_list} projects from labelstudio.")
    return project_list 


def image_ls_projfile_action(project_id):
    # gets the list of images in the project and returns it as a json file
    logger.info("This is the main function for the labelstudio image processing module.")

    if not project_id:
        logger.error("Project ID is required.")
        raise ValueError("Project ID is required.")

    # get the project file from labelstudio
    ls = LabelStudio(base_url=config["api"]["labels_url"], api_key=LABEL_STUDIO_TOKEN)
    tasks = list(ls.tasks.list(project=project_id))
    logger.info(f"Retrieved {tasks} tasks from labelstudio project {project_id}.")
    logger.info(f"Exported project {project_id} from labelstudio.")
    image_dir = "images/incoming"
    get_images_ondisk_results = get_images_ondisk(image_dir)
    
    disk_images = [item["name"] for item in get_images_ondisk_results['extra'][0]['extra']]
    task_images = []
    ls_mapping = {}
    for task in tasks:
        filename = task['data']['image'].split("/")[-1]
        ls_mapping[filename] = task.id
    
    for filename in disk_images:
        if filename in ls_mapping:
            task_images.append({"filename": filename, "task_id": ls_mapping[filename]})
        else:
            task_images.append({"filename": filename, "task_id": None})
    return task_images
