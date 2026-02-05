import requests

from lib.helpers import setup_logger, get_config

logger = setup_logger()
config = get_config()


def grab_dir_list(path: str) -> list:
    """
    grab the autoindex from images.wopr for the dir
    """
    results = []
    debug_vars = []
    logger.info("Starting grab_dir_list()")
    logger.debug(f"Debug vars: {debug_vars}")

    url = f"{config['api']['images_url']}/{path}"
    debug_vars.append(f"url: {url}")
    logger.info(f"Grabbing directory listing from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response_results = response.json()
        logger.info(f"Successfully retrieved directory listing from {url}")
        debug_vars.append(f"response_results: {response_results}")
        results.append(
            {
                "status": "success",
                "message": "retrieved directory listing",
                "extra": response_results,
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving directory listing from {url}: {e}")
        results.append(
            {
                "status": "error",
                "message": f"failed to retrieve directory listing: {e}",
                "extra": [],
            }
        )
    return results


def get_images_ondisk(image_dir: str) -> list:
    """
    list out the files on disk
    select from the available directories:
    - images/incoming
    - images/processed
    """

    results = []
    debug_vars = []
    logger.info("Starting get_images_ondisk()")
    logger.debug(f"Debug vars: {debug_vars}")
    grab_dir_list_results = grab_dir_list(image_dir)
    logger.info("Back to get_images_ondisk after grab_dir_list()")
    debug_vars.append(("grab_dir_list_results", grab_dir_list_results))
    logger.debug(f"Debug vars: {debug_vars}")
    if grab_dir_list_results is None or grab_dir_list_results[0]["status"] != "success":
        logger.error("Error retrieving images on disk")
        logger.debug(f"Debug vars: {debug_vars}")
        results.append(
            {
                "status": "error",
                "message": "failed to retrieve images on disk",
                "extra": {"debug_vars": debug_vars},
            }
        )
    else:
        logger.info("Successfully retrieved images on disk")
        results.append(
            {
                "status": "success",
                "message": "retrieved images on disk",
                "extra": grab_dir_list_results,
            }
        )
        logger.debug(f"Debug vars: {debug_vars}")
    return results


def image_sort(images_db, images_disk):
    """Compare disk images against DB records."""
    logger.info("Starting image_sort()")
    images_both = []
    images_disk_list = []

    # Build set of filenames from DB for fast lookup
    db_filenames = {img.filename for img in images_db}

    logger.debug(f"DB filenames: {db_filenames}")
    logger.debug(f"Images on Disk: {images_disk}")

    for disk_image in images_disk:
        name = disk_image["name"]
        logger.debug(f"Checking disk image: {name}")
        if name in db_filenames:
            logger.debug(f"Image {name} found in both DB and Disk")
            images_both.append(disk_image)
        else:
            images_disk_list.append(disk_image)

    results = [
        {
            "status": "success",
            "message": "sorted images",
            "extra": {"images_both": images_both, "images_disk": images_disk_list},
        }
    ]
    return results
