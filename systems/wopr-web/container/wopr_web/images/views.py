import hashlib
import os

from django.shortcuts import render, redirect

from core.models import Image, ImageGame, Game

from lib.helpers import setup_logger, get_config

from .lib.lib_images import get_images_ondisk, image_sort
from .lib.lib_labelstudio import image_ls_list_projects_action, image_ls_projfile_action

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

            images = Image.objects.all()
            logger.info(f"Retrieved {len(images)} images from DB")
            debug_vars.append(("images", images))
            logger.debug(f"Debug vars: {debug_vars}")

            image_sort_results = image_sort(images, dirs)
            logger.info("Sorted images")
            debug_vars.append(("image_sort_results", image_sort_results))
            logger.debug(f"Debug vars: {debug_vars}")

            images_full = []
            images_on_disk_list = []
            images_on_both_list = []
            for imageondisk in image_sort_results[0]["extra"]["images_disk"]:
                logger.info(f"Image: {imageondisk['name']} - on disk only")
                url = f"{config['api']['images_url']}/{image_dir}/{imageondisk['name']}"
                thumb_url = f"{config['api']['thumbs_url']}/insecure/resize:fill:300:200/plain/{config['api']['images_url']}/{image_dir}/{imageondisk['name']}"
                imageondisk["url"] = url
                imageondisk["thumb_url"] = thumb_url
                imageondisk["path"] = f"{image_dir}/{imageondisk['name']}"
                images_on_disk_list.append(imageondisk)
            for imageinboth in image_sort_results[0]["extra"]["images_both"]:
                logger.info(f"Image: {imageinboth['name']} - both")
                url = f"{config['api']['images_url']}/{image_dir}/{imageinboth['name']}"
                thumb_url = f"{config['api']['thumbs_url']}/insecure/resize:fill:300:200/plain/{config['api']['images_url']}/{image_dir}/{imageinboth['name']}"
                imageinboth["url"] = url
                imageinboth["thumb_url"] = thumb_url
                imageinboth["path"] = f"{image_dir}/{imageinboth['name']}"
                images_on_both_list.append(imageinboth)

            debug_vars.append(("images_full", images_full))
            logger.debug(f"Debug vars: {debug_vars}")
            context = {
                "image_dir": image_dir,
                "dirs": dirs,
                "images_on_disk": images_on_disk_list,
                "images_in_both": images_on_both_list,
                "images_url": config["api"]["images_url"],
                "thumbs_url": config["api"]["thumbs_url"],
            }
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
    results = []
    debug_vars = []
    images = []
    logger.info("Rendering images in DB page")

    try:
        images = Image.objects.all()
        debug_vars.append(("images", images))
        results.append(
            {
                "status": "success",
                "message": f"Retrieved {len(images)} images from DB",
                "extra": {"debug_vars": debug_vars},
            }
        )
        # FIX: results merged into context instead of passed as 4th positional arg to render()
        context = {"images": images, "results": results}
        return render(request, "images_indb.html", context)
    except Exception as e:
        logger.error(f"Error retrieving images from DB: {e}")
        context = {"error": str(e)}
        debug_vars.append(("context", context))
        results.append(
            {
                "status": "error",
                "message": f"Retrieved {len(images)} images from DB",
                "extra": {"context": context},
            }
        )
        # FIX: results merged into context instead of passed as 4th positional arg to render()
        context["results"] = results
        return render(request, "images_indb.html", context)


def add_images_to_db(request):  # plural
    results = []
    debug_vars = []

    if request.method == "POST":
        selected_images = request.POST.getlist("selected_images")
        image_dir = request.POST.get("image_dir")

        debug_vars.append(("selected_images", selected_images))
        debug_vars.append(("image_dir", image_dir))
        logger.info(f"Processing {len(selected_images)} images from {image_dir}")

        # FIX: action fetched once outside the loop - it doesn't change per iteration
        action = request.POST.get("action")

        added_count = 0
        for image_name in selected_images:
            try:
                image_path = f"{image_dir}/{image_name}"
                full_path = f"{config['storage']['base_path']}/{image_path}"

                # Validate file exists
                if not os.path.isfile(full_path):
                    logger.warning(f"File not found: {full_path}")
                    results.append(
                        {"status": "error", "message": f"File not found: {image_name}"}
                    )
                    continue

                if action == "add_to_db":
                    # Generate checksum from file contents
                    with open(full_path, "rb") as f:
                        checksum = hashlib.sha256(f.read()).hexdigest()

                    # Check for duplicate
                    if Image.objects.filter(checksum=checksum).exists():
                        logger.info(f"Duplicate checksum, skipping: {image_name}")
                        results.append(
                            {"status": "warning", "message": f"Duplicate: {image_name}"}
                        )
                        continue

                    # Create record
                    new_image = Image(
                        filename=image_name, artifact_uri=image_path, checksum=checksum
                    )
                    new_image.save()
                    added_count += 1
                    logger.info(f"Added to DB: {image_name}")
                elif action == "move_to_archive":
                    # FIX: use archive_subdir consistently (was archive_path in move_images_to_archive)
                    archive_path = f"{config['storage']['base_path']}/{config['storage']['images_subdir']}/{config['storage']['archive_subdir']}/{image_name}"
                    try:
                        os.rename(full_path, archive_path)
                    except Exception as e:
                        logger.error(f"Failed to move {image_name} to archive: {e}")
                        results.append(
                            {
                                "status": "error",
                                "message": f"Failed to move {image_name} to archive: {str(e)}",
                            }
                        )
                        return render(
                            request, "images_results.html", {"results": results}
                        )
                    logger.info(f"Moved {image_name} to archive")
                    results.append(
                        {
                            "status": "success",
                            "message": f"Moved to archive: {image_name}",
                        }
                    )

            except Exception as e:
                logger.error(f"Failed to add {image_name}: {e}")
                results.append(
                    {"status": "error", "message": f"Failed: {image_name} - {str(e)}"}
                )

        logger.info(f"Successfully added {added_count}/{len(selected_images)} images")
        results.append(
            {"status": "success", "message": f"Added {added_count} images to DB"}
        )

    return render(request, "images_results.html", {"results": results})


def images_ls_list_projects(request):
    logger.info("Rendering image labelstudio page")
    results = []
    action_results = image_ls_list_projects_action(request)
    results.append(
        {
            "status": "success",
            "message": "Rendered image labelstudio page",
            "extra": {"action_results": action_results},
        }
    )
    context = {"projects": action_results}
    return render(request, "image_ls_list_projects.html", context)


def images_ls_projfile(request):
    logger.info("Rendering image labelstudio project file page")
    debug_vars = []
    results = []
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        logger.info(f"Selected project ID: {project_id}")
        # Here you would add logic to retrieve and display the project file based on the selected project ID
        context = {"project_id": project_id}
        image_ls_projfile_results = image_ls_projfile_action(project_id)
        context["task_images"] = image_ls_projfile_results

        return render(request, "image_ls_projfile.html", context)
    else:
        logger.warning("No project ID selected")
        return render(
            request, "image_ls_projfile.html", {"error": "No project ID selected"}
        )


def move_images_to_archive(request):
    results = []
    debug_vars = []

    if request.method == "POST":
        selected_images = request.POST.getlist("selected_images")
        image_dir = request.POST.get("image_dir")

        debug_vars.append(("selected_images", selected_images))
        debug_vars.append(("image_dir", image_dir))
        logger.info(f"Processing {len(selected_images)} images from {image_dir}")

        added_count = 0
        for image_name in selected_images:
            try:
                image_path = f"{image_dir}/{image_name}"
                full_path = f"{config['storage']['base_path']}/{image_path}"

                # Validate file exists
                if not os.path.isfile(full_path):
                    logger.warning(f"File not found: {full_path}")
                    results.append(
                        {"status": "error", "message": f"File not found: {image_name}"}
                    )
                    continue

                # FIX: use archive_subdir to match add_images_to_db (was archive_path)
                archive_path = f"{config['storage']['base_path']}/{config['storage']['images_subdir']}/{config['storage']['archive_subdir']}/{image_name}"
                os.rename(full_path, archive_path)
                logger.info(f"Moved {image_name} to archive")
                results.append(
                    {"status": "success", "message": f"Moved to archive: {image_name}"}
                )
            except Exception as e:
                logger.error(f"Failed to move {image_name} to archive: {e}")
                results.append(
                    {
                        "status": "error",
                        "message": f"Failed to move {image_name} to archive: {str(e)}",
                    }
                )

    # FIX: added missing return statement - was falling off the end with no response
    return render(request, "images_results.html", {"results": results})


def images_games_index(request):
    # Need name, image_total
    image_game_data = []
    results = []
    games = Game.objects.all()
    images = Image.objects.all()
    image_games = ImageGame.objects.all()
    for game in games:
        image_game_data.append(
            {
                "id": game.id,
                "name": game.name,
                "images": ImageGame.objects.filter(game=game),
            }
        )
    # FIX: single query instead of N+1 (one ImageGame filter per image in loop)
    images_not_assigned_to_a_game = Image.objects.filter(imagegame__isnull=True)

    if image_game_data is not None:
        results = {
            "status": "success",
            "message": "Retrieved image game data successfully",
        }
    else:
        results = {
            "status": "error",
            "message": "Failed to retrieve image game data",
        }
    return render(
        request,
        "image_games_index.html",
        {
            "results": results,
            "image_game_data": image_game_data,
            "images_not_assigned_to_a_game": images_not_assigned_to_a_game,
        },
    )


def images_games_details(request, game_id):
    images = []
    images_list = []
    results = []
    url = f"{config['api']['images_url']}"
    # FIX: thumb_url_base extracted so it isn't clobbered on first loop iteration
    thumb_url_base = f"{config['api']['thumbs_url']}/insecure/resize:fill:300:200/plain"
    if game_id != 0:
        images = Image.objects.filter(imagegame__game_id=game_id)
        game = Game.objects.filter(id=game_id).first()
        games = Game.objects.all()
        for image in images:
            spec_url = f"{url}/images/games/{game.shortname}/{image.filename}"
            image_full_url = spec_url
            # FIX: removed stray $ (was f"{thumb_url}/${spec_url}" - literal dollar sign, not interpolation)
            # FIX: use thumb_url_base so it doesn't compound across iterations
            thumb_url = f"{thumb_url_base}/{spec_url}"
            images_list.append(
                {
                    "image_full_url": image_full_url,
                    "thumb_url": thumb_url,
                    "filename": image.filename,
                }
            )
        return render(
            request,
            "image_games_details.html",
            {"images_list": images_list, "games": games, "game": game},
        )
    else:
        images = Image.objects.filter(imagegame__isnull=True)
        if len(images) == 0:
            results.append(
                {
                    "status": "error",
                    "message": f"No images available; game_id is {game_id}",
                }
            )
        games = Game.objects.all()
        for image in images:
            spec_url = f"{url}/images/incoming/{image.filename}"
            image_full_url = spec_url
            # FIX: same thumb_url fixes applied to else branch
            thumb_url = f"{thumb_url_base}/{spec_url}"
            images_list.append(
                {
                    "image_full_url": image_full_url,
                    "thumb_url": thumb_url,
                    "filename": image.filename,
                }
            )
        return render(
            request,
            "image_games_details.html",
            {"images_list": images_list, "games": games},
        )
    # NOTE: the two lines below this were unreachable dead code - removed


def change_image_game(request):
    results = []
    logger.info("Change image game request received")
    if request.method == "POST":
        logger.info("Processing POST request - change_image_game")
        selected_images = request.POST.getlist("selected_images")
        game_id = request.POST.get("game")
        if selected_images and game_id:
            game = Game.objects.filter(id=game_id).first()
            if game:
                for image_name in selected_images:
                    # FIX: filter on 'filename' field to match model usage elsewhere (was 'name')
                    image = Image.objects.filter(filename=image_name).first()
                    if image:
                        ImageGame.objects.update_or_create(
                            image=image, defaults={"game": game}
                        )
                results.append(
                    {"status": "success", "message": "Images updated successfully"}
                )
            else:
                results.append({"status": "error", "message": "Invalid game"})
                return redirect("image_games_index")
        else:
            results.append(
                {"status": "error", "message": "No images selected or invalid game"}
            )
    else:
        logger.info(f"No post: {request}")
    if not results:
        results.append(
            {"status": "error", "message": f"Dropped right through request {request}"}
        )
    return render(request, "images_results.html", {"results": results})
