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
        dir_selector.append(
            {
                "name": f"images_{dir_key} - {dirs['WOPRS']['images'][dir_key]}",
                "dir_key": dir_key,
                "path": dirs["WOPRS"]["images"][dir_key],
            }
        )
    context = {"dir_selector": dir_selector}
    debug_vars.append(("dir_selector", dir_selector))
    logger.debug(f"Debug vars: {debug_vars}")
    return render(request, "images_dir_selector.html", context)


def images_ondisk(request):
    logger.info("Rendering images on disk page")
    context = []
    results = []
    debug_vars = []
    if request.method == "POST":
        image_dir = request.POST.get("image_dir")
        debug_vars.append(("image_dir", image_dir))
        logger.info(f"Selected image directory: {image_dir}")
        logger.debug(f"Debug vars: {debug_vars}")

        get_images_ondisk_results = get_images_ondisk(image_dir)
        debug_vars.append(("get_images_ondisk_results", get_images_ondisk_results))
        logger.debug(f"Debug vars: {debug_vars}")

        if get_images_ondisk_results["status"] != "success":
            results.append(get_images_ondisk_results)
            render(request, "images_results.html", {"results": results})

    return render(request, "images_ondisk.html", context)


def images_indb(request):
    logger.info("Rendering images in DB page")
    return render(request, "images_indb.html")
