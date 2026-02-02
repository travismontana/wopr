import threading

from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from core.models import ModelVersion, ModelInfo, TrainingRun, Dataset, Result

from .lib.lib_training import list_all_projects, get_training_uuid

from lib.helpers import setup_logger, call_model_control

logger = setup_logger()


# Create your views here.
def index(request):
    models = ModelInfo.objects.all()
    model_vers = ModelVersion.objects.all()
    training_runs = TrainingRun.objects.all()
    logger.info(f"views.py - Retrieved {models.count()} models from the database.")
    logger.debug(f"Models: {models}")
    results, projects = list_all_projects()
    if results is not None:
        for result in results:
            if result["status"] == "error":
                logger.error(f"views.py - Error: {result['message']}")
            else:
                logger.info(f"views.py - Success: {result['message']}")
    logger.info(f"views.py - Retrieved {len(projects)} projects.")
    logger.debug(f"Projects: {projects}")
    context = {
        "models": models,
        "projects": projects,
        "model_vers": model_vers,
        "training_runs": training_runs,
    }
    return render(request, "training.html", context)


def new_training(request):
    models = ModelInfo.objects.all()
    model_vers = ModelVersion.objects.all()
    training_runs = TrainingRun.objects.all()
    logger.info(f"views.py - Retrieved {models.count()} models from the database.")
    logger.debug(f"Models: {models}")
    results, projects = list_all_projects()
    if results is not None:
        for result in results:
            if result["status"] == "error":
                logger.error(f"views.py - Error: {result['message']}")
            else:
                logger.info(f"views.py - Success: {result['message']}")
    logger.info(f"views.py - Retrieved {len(projects)} projects.")
    logger.debug(f"Projects: {projects}")
    context = {
        "models": models,
        "projects": projects,
        "model_vers": model_vers,
        "training_runs": training_runs,
    }
    return render(request, "training_new.html", context)


def start_training(request):
    """Start training with selected model version and project."""
    if request.method == "POST":
        version_id = request.POST.get("version_id")
        project_id = request.POST.get("project_id")
        description = request.POST.get("description", "")
        notes = request.POST.get("notes", "")

        if not version_id or not project_id:
            logger.error("Missing version_id or project_id in POST data")
            return render(
                request, "training.html", {"error": "Missing required fields"}
            )

        try:
            version = ModelVersion.objects.get(id=version_id)
            logger.info(
                f"Starting training for version {version_id} on project {project_id}"
            )
            training, results = get_training_uuid(
                version, project_id, description, notes
            )
            logger.info(f"Training started with UUID: {training.uuid}")
            return render(request, "training.html", {"results": results})
        except ModelVersion.DoesNotExist:
            logger.error(f"ModelVersion {version_id} not found")
            return render(request, "training.html", {"error": "Invalid model version"})
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return render(request, "training.html", {"error": str(e)})

    return redirect("index")


def training_detail(request):
    if request.method == "POST":
        run_id = request.POST.get("run_id")
        try:
            needs = []
            training_run = TrainingRun.objects.get(id=run_id)
            dataset = Dataset.objects.get(id=training_run.dataset.id)
            result = Result.objects.get(id=training_run.result.id)
            if "/dev/null" in dataset.artifact_uri:
                needs.append({"set": "dataset", "needs": "artifact_uri"})
            if "/dev/null" in result.artifact_uri:
                needs.append({"set": "result", "needs": "artifact_uri"})
            logger.info(f"Retrieved details for TrainingRun ID: {run_id}")
            logger.debug(
                f"TrainingRun: {training_run}, Dataset: {dataset}, Result: {result}, Needs: {needs}"
            )
            context = {
                "training_run": training_run,
                "dataset": dataset,
                "result": result,
                "needs": needs,
            }
            return render(request, "training_detail.html", context)
        except TrainingRun.DoesNotExist:
            logger.error(f"TrainingRun {run_id} not found")
            return render(
                request, "training.html", {"error": "Invalid training run ID"}
            )
    return render(request, "training.html", {"error": "Invalid training run ID"})


def generate_dataset(request):

    """Generate dataset from Label Studio project."""
    logger.info("Dataset generation requested")
    results = []

    if request.method == "POST":
        dataset_uuid = request.POST.get("dataset_uuid")

        try:
            dataset = Dataset.objects.get(uuid=dataset_uuid)
            logger.info(f"Generating dataset with UUID: {dataset_uuid}")

            payload = {
                "action": "generate_dataset",
                "dataset_uuid": str(dataset.uuid),
                "dataset": model_to_dict(dataset),
            }

            # Fire and forget - don't wait for response

            def async_call():
                try:
                    logger.info(
                        f"Background: Starting dataset generation for {dataset_uuid}"
                    )
                    dataz = call_model_control(payload)
                    logger.info(f"Background: Dataset generation response: {dataz}")
                except Exception as e:
                    logger.error(f"Background: Dataset generation failed: {e}")

            thread = threading.Thread(target=async_call)
            thread.daemon = True
            thread.start()

            results.append(
                {
                    "status": "success",
                    "type": "dataset_generation",
                    "message": f"Dataset generation started for UUID: {dataset_uuid}. Check logs for completion.",
                }
            )

        except Dataset.DoesNotExist:
            logger.error(f"Dataset with UUID {dataset_uuid} not found")
            results.append(
                {
                    "status": "error",
                    "type": "dataset_generation",
                    "message": f"Dataset with UUID {dataset_uuid} not found",
                }
            )
        except Exception as e:
            logger.error(f"Dataset generation failed: {e}")
            results.append(
                {
                    "status": "error",
                    "type": "dataset_generation",
                    "message": f"Dataset generation failed: {str(e)}",
                }
            )
    else:
        logger.error("Invalid request method for dataset generation")
        results.append(
            {
                "status": "error",
                "type": "dataset_generation",
                "message": "Invalid request method",
            }
        )

    return render(request, "training_return.html", {"results": results})
