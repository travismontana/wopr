import hashlib
import os
import shutil  # ++ added for shutil.copy2 ++
from urllib.parse import parse_qs, urlparse

from django.shortcuts import render, redirect

from core.models import Game, GameLabelproj, Image, ImageGame
from lib.helpers import get_config, setup_logger
from .lib.lib_images import get_images_ondisk, image_sort
from .lib.lib_labelstudio import (
    image_ls_list_projects_action,
    image_ls_projfile_action,
    send_labelstudio,
)

logger = setup_logger()
config = get_config()

BASE_PATH = config["storage"]["base_path"]

IMAGES_SUBDIR = config["storage"]["images_subdir"]
INCOMING_SUBDIR = config["storage"]["incoming_subdir"]
ARCHIVE_SUBDIR = config["storage"]["archive_subdir"]
GAMES_SUBDIR = "games"
BACKUPS_SUBDIR = "backups"
LABEL_SUBDIR = config["storage"]["label_subdir"]
LABEL_SOURCE_SUBDIR = config["storage"]["label_source_subdir"]
LABEL_TARGET_SUBDIR = config["storage"]["label_target_subdir"]

MODELS_SUBDIR = config["storage"]["models_subdir"]
WEIGHTS_SUBDIR = config["storage"]["weights_subdir"]
RUNS_SUBDIR = config["storage"]["runs_subdir"]
DISTFILES_SUBDIR = config["storage"]["distfiles_subdir"]
BACKUPS_SUBDIR = config["storage"]["backups_subdir"]
MODELS_ARCHIVE_SUBDIR = config["storage"]["archive_subdir"]

IMAGES_URL = config["api"]["images_url"]
THUMBS_URL = config["api"]["thumbs_url"]
THUMB_URL_BASE = f"{THUMBS_URL}/insecure/resize:fill:300:200/plain"

WOPRS = {
    "images": {
        "incoming": f"{BASE_PATH}/{IMAGES_SUBDIR}/{INCOMING_SUBDIR}",
        "archive": f"{BASE_PATH}/{IMAGES_SUBDIR}/{ARCHIVE_SUBDIR}",
        "games": f"{BASE_PATH}/{IMAGES_SUBDIR}/{GAMES_SUBDIR}",
        "backups": f"{BASE_PATH}/{IMAGES_SUBDIR}/{BACKUPS_SUBDIR}",
    },
    "ls": {
        "source": f"{BASE_PATH}/{LABEL_SUBDIR}/{LABEL_SOURCE_SUBDIR}",
        "target": f"{BASE_PATH}/{LABEL_SUBDIR}/{LABEL_TARGET_SUBDIR}",
        "games": f"{BASE_PATH}/{LABEL_SUBDIR}",
    },
    "models": {
        "weights": f"{BASE_PATH}/{MODELS_SUBDIR}/{WEIGHTS_SUBDIR}",
        "runs": f"{BASE_PATH}/{MODELS_SUBDIR}/{RUNS_SUBDIR}",
        "distfiles": f"{BASE_PATH}/{MODELS_SUBDIR}/{DISTFILES_SUBDIR}",
        "backups": f"{BASE_PATH}/{MODELS_SUBDIR}/{BACKUPS_SUBDIR}",
        "archive": f"{BASE_PATH}/{MODELS_SUBDIR}/{MODELS_ARCHIVE_SUBDIR}",
    },
}


def images_index(request):
    logger.info("Rendering image index page")
    return render(request, "image_index.html")


def show_dir_selector(request):
    logger.info("Rendering directory selector")

    dir_selector = []
    for dir_key, full_path in WOPRS["images"].items():
        rel_path = full_path.split(f"{BASE_PATH}/")[-1]
        dir_selector.append(
            {
                "name": f"images_{rel_path}",
                "dir_key": dir_key,
                "path": rel_path,
            }
        )

    return render(request, "images_dir_selector.html", {"dir_selector": dir_selector})


def images_ondisk(request):
    logger.info("Starting images_ondisk view")
    results = []
    debug_vars = []

    if request.method != "POST":
        logger.warning("No image directory selected")
        results.append(
            {
                "status": "warning",
                "message": "no image directory selected",
                "extra": {"debug_vars": debug_vars},
            }
        )
        return render(request, "images_results.html", {"results": results})

    image_dir = request.POST.get("image_dir")
    debug_vars.append(("image_dir", image_dir))
    logger.info("Selected image directory: %s", image_dir)

    get_images_ondisk_results = get_images_ondisk(image_dir)
    debug_vars.append(("get_images_ondisk_results", get_images_ondisk_results))

    if (
        not get_images_ondisk_results
        or get_images_ondisk_results[0].get("status") != "success"
    ):
        logger.error("Error retrieving images on disk")
        results.append(
            {
                "status": "error",
                "message": "get_images_ondisk(image_dir) failed",
                "extra": {"debug_vars": debug_vars},
            }
        )
        return render(request, "images_results.html", {"results": results})

    dirs = []
    for res in get_images_ondisk_results[0].get("extra", []):
        if "retrieved directory listing" in res.get("message", ""):
            dirs = res.get("extra", [])
            break
    debug_vars.append(("dirs", dirs))

    images = Image.objects.all()
    debug_vars.append(("images_count", images.count()))

    image_sort_results = image_sort(images, dirs)
    debug_vars.append(("image_sort_results", image_sort_results))

    extra = image_sort_results[0].get("extra", {}) if image_sort_results else {}
    images_disk = extra.get("images_disk", [])
    images_both = extra.get("images_both", [])

    def enrich(image_obj):
        name = image_obj["name"]
        url = f"{IMAGES_URL}/{image_dir}/{name}"
        thumb_url = f"{THUMB_URL_BASE}/{IMAGES_URL}/{image_dir}/{name}"
        return {
            **image_obj,
            "url": url,
            "thumb_url": thumb_url,
            "path": f"{image_dir}/{name}",
        }

    images_on_disk_list = [enrich(i) for i in images_disk]
    images_on_both_list = [enrich(i) for i in images_both]

    context = {
        "image_dir": image_dir,
        "dirs": dirs,
        "images_on_disk": images_on_disk_list,
        "images_in_both": images_on_both_list,
        "images_url": IMAGES_URL,
        "thumbs_url": THUMBS_URL,
    }
    return render(request, "images_ondisk.html", context)


def images_indb(request):
    logger.info("Rendering images in DB page")
    results = []

    try:
        images = Image.objects.all()
        results.append(
            {
                "status": "success",
                "message": f"Retrieved {images.count()} images from DB",
            }
        )
        return render(
            request,
            "images_indb.html",
            {"images": images, "results": results},
        )
    except Exception as exc:
        logger.exception("Error retrieving images from DB")
        results.append(
            {
                "status": "error",
                "message": f"Error retrieving images from DB: {exc}",
            }
        )
        return render(
            request,
            "images_indb.html",
            {"images": [], "results": results, "error": str(exc)},
        )


def add_images_to_db(request):
    results = []

    if request.method != "POST":
        return render(request, "images_results.html", {"results": results})

    selected_images = request.POST.getlist("selected_images")
    image_dir = request.POST.get("image_dir")
    action = request.POST.get("action")

    logger.info(
        "Processing %d images from %s action=%s",
        len(selected_images),
        image_dir,
        action,
    )

    added_count = 0

    for image_name in selected_images:
        image_path = f"{image_dir}/{image_name}"
        full_path = f"{BASE_PATH}/{image_path}"

        if not os.path.isfile(full_path):
            logger.warning("File not found: %s", full_path)
            results.append(
                {"status": "error", "message": f"File not found: {image_name}"}
            )
            continue

        try:
            if action == "add_to_db":
                with open(full_path, "rb") as f:
                    checksum = hashlib.sha256(f.read()).hexdigest()

                if Image.objects.filter(checksum=checksum).exists():
                    results.append(
                        {"status": "warning", "message": f"Duplicate: {image_name}"}
                    )
                    continue

                Image.objects.create(
                    filename=image_name,
                    artifact_uri=image_path,
                    checksum=checksum,
                )
                added_count += 1
                results.append(
                    {"status": "success", "message": f"Added to DB: {image_name}"}
                )

            elif action == "unarchive":
                archive_path = (
                    f"{BASE_PATH}/{IMAGES_SUBDIR}/{ARCHIVE_SUBDIR}/{image_name}"
                )
                incoming_path = (
                    f"{BASE_PATH}/{IMAGES_SUBDIR}/{INCOMING_SUBDIR}/{image_name}"
                )
                os.rename(archive_path, incoming_path)
                results.append(
                    {"status": "success", "message": f"Unarchived: {image_name}"}
                )

            elif action == "move_to_archive":
                archive_path = (
                    f"{BASE_PATH}/{IMAGES_SUBDIR}/{ARCHIVE_SUBDIR}/{image_name}"
                )
                os.rename(full_path, archive_path)
                results.append(
                    {"status": "success", "message": f"Moved to archive: {image_name}"}
                )

            else:
                results.append(
                    {"status": "error", "message": f"Unknown action: {action}"}
                )

        except Exception as exc:
            logger.exception("Action failed for %s", image_name)
            results.append(
                {"status": "error", "message": f"Failed: {image_name} - {exc}"}
            )

    if action == "add_to_db":
        results.append(
            {"status": "success", "message": f"Added {added_count} images to DB"}
        )

    return render(request, "images_results.html", {"results": results})


def images_ls_list_projects(request):
    logger.info("Rendering image labelstudio page")
    projects = image_ls_list_projects_action(request)
    return render(request, "image_ls_list_projects.html", {"projects": projects})


def images_ls_projfile(request):
    logger.info("Rendering image labelstudio project file page")

    if request.method != "POST":
        logger.warning("No project ID selected")
        return render(
            request, "image_ls_projfile.html", {"error": "No project ID selected"}
        )

    project_id = request.POST.get("project_id")
    logger.info("Selected project ID: %s", project_id)

    task_images = image_ls_projfile_action(project_id)
    return render(
        request,
        "image_ls_projfile.html",
        {"project_id": project_id, "task_images": task_images},
    )


def move_images_to_archive(request):
    results = []

    if request.method != "POST":
        return render(request, "images_results.html", {"results": results})

    selected_images = request.POST.getlist("selected_images")
    image_dir = request.POST.get("image_dir")
    logger.info("Processing %d images from %s", len(selected_images), image_dir)

    for image_name in selected_images:
        image_path = f"{image_dir}/{image_name}"
        full_path = f"{BASE_PATH}/{image_path}"

        if not os.path.isfile(full_path):
            results.append(
                {"status": "error", "message": f"File not found: {image_name}"}
            )
            continue

        archive_path = f"{BASE_PATH}/{IMAGES_SUBDIR}/{ARCHIVE_SUBDIR}/{image_name}"
        try:
            os.rename(full_path, archive_path)
            results.append(
                {"status": "success", "message": f"Moved to archive: {image_name}"}
            )
        except Exception as exc:
            logger.exception("Failed to move %s to archive", image_name)
            results.append(
                {"status": "error", "message": f"Failed to move {image_name}: {exc}"}
            )

    return render(request, "images_results.html", {"results": results})


def images_games_index(request):
    games = Game.objects.all()

    image_game_data = []
    for game in games:
        qs = ImageGame.objects.filter(game=game)
        image_game_data.append(
            {
                "id": game.id,
                "name": game.name,
                "images": qs,
                "num_images_total": qs.count(),
            }
        )

    images_not_assigned_to_a_game = Image.objects.filter(imagegame__isnull=True)

    results = {
        "status": "success",
        "message": "Retrieved image game data successfully",
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
    url_base = IMAGES_URL

    if game_id != 0:
        glp = GameLabelproj.objects.filter(game_id=game_id).first()
        if not glp:
            return render(
                request,
                "image_games_details.html",
                {
                    "images_list": [],
                    "games": Game.objects.all(),
                    "error": "No LS project mapped",
                },
            )

        ls_project_id = glp.ls_project_id
        if ls_project_id == "" or ls_project_id is None:
            return render(
                request,
                "images_results.html",
                {
                    "results": {
                        "status": "error",
                        "message": f"No LS project mapped glp: {glp}",
                    }
                },
            )

        game = Game.objects.filter(id=game_id).first()
        games = Game.objects.all()
        images = Image.objects.filter(imagegame__game_id=game_id)

        tasks = image_ls_projfile_action(ls_project_id) or []
        task_filenames = set()

        for task in tasks:
            image_url = task.get("data", {}).get("image", "")
            parsed = urlparse(image_url)
            d_param = parse_qs(parsed.query).get("d", [""])[0]
            task_filenames.add(d_param.split("/")[-1])

        images_list = []
        images_not_in_tasks = []

        for image in images:
            spec_url = f"{url_base}/images/games/{game.shortname}/{image.filename}"
            images_list.append(
                {
                    "image_full_url": spec_url,
                    "thumb_url": f"{THUMB_URL_BASE}/{spec_url}",
                    "filename": image.filename,
                }
            )
            if image.filename not in task_filenames:
                images_not_in_tasks.append(
                    {
                        "image_full_url": spec_url,
                        "thumb_url": f"{THUMB_URL_BASE}/{spec_url}",
                        "filename": image.filename,
                        "ls_project_id": ls_project_id,
                    }
                )

        return render(
            request,
            "image_games_details.html",
            {
                "images_list": images_list,
                "games": games,
                "game": game,
                "tasks": tasks,
                "images_not_in_tasks": images_not_in_tasks,
                "ls_project_id": ls_project_id,
            },
        )

    # game_id == 0 => unassigned
    images = Image.objects.filter(imagegame__isnull=True)
    games = Game.objects.all()

    images_list = []
    for image in images:
        spec_url = f"{url_base}/images/incoming/{image.filename}"
        images_list.append(
            {
                "image_full_url": spec_url,
                "thumb_url": f"{THUMB_URL_BASE}/{spec_url}",
                "filename": image.filename,
            }
        )

    return render(
        request,
        "image_games_details.html",
        {"images_list": images_list, "games": games},
    )


def change_image_game(request):
    results = []
    logger.info("Change image game request received")

    if request.method != "POST":
        results.append({"status": "error", "message": "Invalid method"})
        return render(request, "images_results.html", {"results": results})

    selected_images = request.POST.getlist("selected_images")
    new_game_id = request.POST.get("new_game")
    game_id = request.POST.get("current_game")

    if not selected_images or not new_game_id:
        results.append(
            {"status": "error", "message": "No images selected or invalid game"}
        )
        return render(request, "images_results.html", {"results": results})

    old_game = Game.objects.filter(id=game_id).first() if game_id else None
    new_game = Game.objects.filter(id=new_game_id).first()

    if not new_game:
        results.append({"status": "error", "message": "New game not found"})
        return render(request, "images_results.html", {"results": results})

    game_path = f"{BASE_PATH}/{IMAGES_SUBDIR}/games"

    for image_name in selected_images:
        image = Image.objects.filter(filename=image_name).first()
        if not image:
            results.append(
                {"status": "error", "message": f"Image not found in DB: {image_name}"}
            )
            continue

        ImageGame.objects.update_or_create(image=image, defaults={"game": new_game})

        dest_path = f"{game_path}/{new_game.shortname}/{image_name}"
        if not old_game:
            source_path = f"{BASE_PATH}/{IMAGES_SUBDIR}/{INCOMING_SUBDIR}/{image_name}"
        else:
            source_path = f"{game_path}/{old_game.shortname}/{image_name}"

        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            os.rename(source_path, dest_path)
            results.append(
                {
                    "status": "success",
                    "message": f"Moved {image_name} to {new_game.shortname}",
                }
            )
        except OSError as exc:
            logger.exception("Error moving image %s", image_name)
            results.append(
                {"status": "error", "message": f"Error moving {image_name}: {exc}"}
            )

    if not results:
        results.append({"status": "error", "message": "No changes made"})

    return render(request, "images_results.html", {"results": results})


def add_to_labelstudio(request):
    results = []

    if request.method != "POST":
        results.append({"status": "error", "message": "Invalid method"})
        return render(request, "images_results.html", {"results": results})

    selected_images = request.POST.getlist("selected_images")
    project_id = request.POST.get("project_id")

    logger.info(
        "Adding %d images to Label Studio for project_id: %s",
        len(selected_images),
        project_id,
    )
    if not project_id:
        results.append({"status": "error", "message": "project_id is required"})
        return render(request, "images_results.html", {"results": results})
    # ++ filter on ls_project_id, not project_id (field name fix) ++
    glp = GameLabelproj.objects.filter(ls_project_id=project_id).first()
    if not glp:
        results.append({"status": "error", "message": "Game not found for project"})
        return render(request, "images_results.html", {"results": results})

    game_shortname = glp.game.shortname

    # ++ iterate selected_images; use os.path.join for path construction ++
    # ++ shutil.copy2 preserves metadata and is a copy, not a move ++
    for image_name in selected_images:
        source_file = os.path.join(WOPRS["images"]["games"], game_shortname, image_name)
        dest_file = os.path.join(WOPRS["ls"]["games"], game_shortname, image_name)

        try:
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(source_file, dest_file)
            logger.info("Copied %s to labelstudio staging", image_name)
            results.append(
                {
                    "status": "success",
                    "message": f"Copied {image_name} to labelstudio staging",
                }
            )
        except OSError as exc:
            logger.exception("Error copying image %s", image_name)
            results.append(
                {"status": "error", "message": f"Error copying {image_name}: {exc}"}
            )
            # ++ bail on copy failure before attempting sync ++
            return render(request, "images_results.html", {"results": results})

    # ++ sync only after all copies succeed; redirect only on success ++
    try:
        send_labelstudio(project_id)
    except RuntimeError as exc:
        results.append({"status": "error", "message": str(exc)})
        return render(request, "images_results.html", {"results": results})

    return redirect("images_games_index")
