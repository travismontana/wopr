from core.models import Game, GameLabelproj, Image, ImageGame, MLDatasets
from lib.helpers import get_config, setup_logger

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

def work_datasets_mgmt(game_id):
    """Actual implementation for managing datasets for a specific game"""
    logger.info("Managing datasets for game_id: %s", game_id)
    results = []
    game = Game.objects.get(id=game_id)
    ml_datasets = MLDatasets.objects.filter(game=game)
    logger.info("Found %d datasets for game_id: %s", ml_datasets.count(), game_id)
    results.append({"status": "success", "message": ml_datasets})
    return results