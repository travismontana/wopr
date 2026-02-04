from django.shortcuts import render

from lib.helpers import setup_logger, get_config

from .lib.lib_images import get_images_ondisk

logger = setup_logger()
config = get_config()

WOPRS = {
    "images": {
        "incoming": f"{config['storage']['base_path']}/{config['storage']['images_subdir']}/{config['storage']['incoming_subdir']}",
        "archive": f"{config['storage']['base_path']}/{config['storage']['images_subdir']}/{config['storage']['archive_subdir']}",
        "backups": f"{config['storage']['base_path']}/{config['storage']['images_subdir']}/{config['storage']['backups_subdir']}",
    },
    "ls": {
        "source": f"{config['storage']['base_path']}/{config['storage']['label_subdir']}/{config['storage']['label_source_subdir']}",
        "target": f"{config['storage']['base_path']}/{config['storage']['label_subdir']}/{config['storage']['label_target_subdir']}",
    },
    "models": {
        "weights": f"{config['storage']['base_path']}/{config['storage']['models_subdir']}/{config['storage']['weights_subdir']}",
        "runs": f"{config['storage']['base_path']}/{config['storage']['models_subdir']}/{config['storage']['runs_subdir']}",
        "distfiles": f"{config['storage']['base_path']}/{config['storage']['models_subdir']}/{config['storage']['distfiles_subdir']}",
        "backups": f"{config['storage']['base_path']}/{config['storage']['models_subdir']}/{config['storage']['backups_subdir']}",
        "archive": f"{config['storage']['base_path']}/{config['storage']['models_subdir']}/{config['storage']['archive_subdir']}",
    },
}

# Create your views here.
def images_index(request):
    logger.info("Rendering image index page")
    return render(request, "image_index.html")


def show_dir_selector(request):
    logger.info("Rendering directory selector")
    debug_vars = []
    dirs = {"WOPRS": WOPRS}
    debug_vars.append(("WOPRS", WOPRS))

    dir_selector = []
    for dir_key in dirs["WOPRS"]["images"]:
        d = dirs["WOPRS"]["images"][dir_key].split(
            f"{config['storage']['base_path']}/"
        )[-1]
        dir_selector.append(
            {
                "name": f"images_{d}",
                "dir_key": dir_key,
                "path": d,
            }
        )
    context = {"dir_selector": dir_selector}
    debug_vars.append(("dir_selector", dir_selector))
    logger.debug(f"Debug vars: {debug_vars}")
    return render(request, "images_dir_selector.html", context)


def images_ondisk(request):
    logger.info("Starting images_ondisk view")
    context = []
    results = []
    debug_vars = []
    if request.method == "POST":
        image_dir = request.POST.get("image_dir")
        debug_vars.append(("image_dir", image_dir))
        logger.info(f"Selected image directory: {image_dir}")
        logger.debug(f"Debug vars: {debug_vars}")

        get_images_ondisk_results = get_images_ondisk(image_dir)
        logger.info("Back to images_ondisk after get_images_ondisk()")
        debug_vars.append(("get_images_ondisk_results", get_images_ondisk_results))
        logger.debug(f"Debug vars: {debug_vars}")

        if (
            get_images_ondisk_results is None
            or get_images_ondisk_results[0]["status"] != "success"
        ):
            logger.error("Error retrieving images on disk")
            logger.debug(f"Debug vars: {debug_vars}")
            results.append(
                {
                    "status": "error",
                    "message": "get_images_ondisk_results = get_images_ondisk(image_dir) - failed.",
                    "extra": {"debug_vars": debug_vars},
                }
            )
            return render(request, "images_results.html", {"results": results})

        else:
            logger.info("Successfully retrieved images on disk")
            results.append(
                {
                    "status": "success",
                    "message": "retrieved images on disk",
                    "extra": get_images_ondisk_results,
                }
            )
            for res in get_images_ondisk_results[0]["extra"]:
                logger.info(f"Result: {res['status']} - {res['message']}")
                if "retrieved directory listing" in res["message"]:
                    dirs = res["extra"]
                    debug_vars.append(("dirs", dirs))
            context = {
                "image_dir": image_dir,
                "dirs": dirs,
                "images_url": config["api"]["images_url"],
                "thumbs_url": config["api"]["thumbs_url"],
            }
            logger.debug(f"Debug vars: {debug_vars}")
            return render(request, "images_ondisk.html", context)
    else:
        logger.warning("No image directory selected")
        results.append(
            {
                "status": "warning",
                "message": "no image directory selected",
                "extra": {"debug_vars": debug_vars},
            }
        )
        logger.debug(f"Debug vars: {debug_vars}")

    return render(request, "images_results.html", {"results": results})


def images_indb(request):
    logger.info("Rendering images in DB page")
    return render(request, "images_indb.html")
