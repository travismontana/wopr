import threading

from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from core.models import ModelVersion, ModelInfo, TrainingRun, Dataset, Result

from .lib.lib_training import list_all_projects, get_training_uuid
from django.utils.timezone import now
from lib.helpers import setup_logger, call_model_control
from models.lib.lib_model import call_model_ctl

logger = setup_logger()


# Create your views here.
def index(request):
    models = ModelInfo.objects.all()
    model_vers = ModelVersion.objects.all()
    training_runs = TrainingRun.objects.all()
    logger.info(f"views.py - Retrieved {models.count()} models from the database.")
    logger.debug(f"Models: {models}")
    context = {
        "models": models,
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

            def async_call():
                try:
                    logger.info(
                        f"Background: Starting dataset generation for {dataset_uuid}"
                    )

                    dataz = call_model_control(payload)
                    logger.info(f"Background: Dataset generation response: {dataz}")

                    dataset_obj = Dataset.objects.get(uuid=dataset_uuid)

                    if dataz.get("status") == "success" and "data" in dataz:
                        data = dataz["data"]

                        import json

                        metadata = {
                            "total_tasks": data.get("total_tasks", 0),
                            "images_downloaded": data.get("images_downloaded", 0),
                            "images_failed": data.get("images_failed", 0),
                            "data_yaml": data.get("data_yaml", ""),
                            "dataset_path": data.get("dataset_path", ""),
                            "images_path": data.get("images_path", ""),
                            "yolo_path": data.get("yolo_path", ""),
                        }

                        # Update with YOLO path (the training directory)
                        dataset_obj.artifact_uri = data.get("yolo_path", "")
                        dataset_obj.note = json.dumps(metadata)
                        dataset_obj.save()  # auto_now handles updated_at

                        logger.info(
                            f"Dataset {dataset_uuid} updated: {dataset_obj.artifact_uri}"
                        )
                    else:
                        error_msg = dataz.get("message", "Unknown error")
                        logger.error(f"Dataset generation failed: {error_msg}")
                        import json

                        dataset_obj.note = json.dumps({"error": error_msg})
                        dataset_obj.save()

                except Exception as e:
                    logger.error(f"Background: Dataset generation failed: {e}")
                    try:
                        import json

                        dataset_obj = Dataset.objects.get(uuid=dataset_uuid)
                        dataset_obj.note = json.dumps({"error": str(e)})
                        dataset_obj.save()
                    except Exception as db_error:
                        logger.error(f"Could not update dataset: {db_error}")

            # Actually start the thread
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


def training_setup(request):
    logger.info("Training setup requested")
    if request.method == "POST":
        logger.info("Processing training setup POST request")
        training_run_id = request.POST.get("training_run_id")
        dataset_id = request.POST.get("dataset_id")  # Match form field name
        try:
            logger.info("Trying to retrieve training setup details")
            training_run_obj = TrainingRun.objects.get(id=training_run_id)
            dataset_obj = Dataset.objects.get(id=dataset_id)  # Actually fetch it
            logger.info(
                f"Retrieved TrainingRun ID: {training_run_id}, Dataset ID: {dataset_id}"
            )

            model_id = training_run_obj.model_version.model.id
            model_vers = ModelVersion.objects.get(model=model_id)

            logger.info(
                f"Preparing training setup for Model ID: {model_id}, Dataset ID: {dataset_id}"
            )
            context = {
                "model": model_vers.model,
                "model_ver": model_vers,
                "dataset": dataset_obj,  # Pass actual objects
                "training_run": training_run_obj,
            }
            logger.debug(f"Training setup context: {context}")
            return render(request, "training_setup.html", context)
        except Exception as e:
            logger.error(f"Training setup failed: {e}")
            return render(request, "training.html", {"error": str(e)})
    return redirect("index")


def training_results(request):
    if request.method == "POST":
        logger.info("Processing training results POST request")
        results = []

        dataset_id = request.POST.get("dataset_id")
        model_ver_id = request.POST.get("model_version_id")
        training_run_id = request.POST.get("training_run_id")

        logger.info(
            f"Received IDs - Dataset: {dataset_id}, ModelVersion: {model_ver_id}, TrainingRun: {training_run_id}"
        )

        try:
            # Fetch objects to validate and get fields
            dataset_obj = Dataset.objects.get(id=dataset_id)
            model_ver_obj = ModelVersion.objects.get(id=model_ver_id)
            training_run_obj = TrainingRun.objects.get(id=training_run_id)

            training_params = {
                "epochs": int(request.POST.get("epochs", 100)),
                "batch_size": int(request.POST.get("batch_size", 16)),
                "imgsz": int(request.POST.get("imgsz", 640)),
                "patience": int(request.POST.get("patience", 50)),
            }

            logger.info(f"Starting training for TrainingRun ID: {training_run_id}")

            # Build JSON-safe payload with only needed fields
            payload = {
                "action": "train",
                "dataset": {
                    "id": dataset_obj.id,
                    "uuid": str(dataset_obj.uuid),
                    "artifact_uri": dataset_obj.artifact_uri,
                    "project_id": dataset_obj.project_id,
                },
                "model_version": {
                    "id": model_ver_obj.id,
                    "version": model_ver_obj.version,
                    "artifact_uri": model_ver_obj.artifact_uri,
                    "model_id": model_ver_obj.model.id,
                    "model_name": model_ver_obj.model.name,
                },
                "training_run": {
                    "id": training_run_obj.id,
                    "uuid": str(training_run_obj.uuid),
                },
                "training_params": training_params,
            }

            def async_call():
                try:
                    logger.info(
                        f"Background: Starting training for TrainingRun ID: {training_run_id}"
                    )

                    training_response = call_model_ctl(payload)
                    logger.info(f"Training response: {training_response}")

                    # Update TrainingRun or Result based on response
                    training_run_update = TrainingRun.objects.get(id=training_run_id)

                    if (
                        training_response.get("status") == "success"
                        and "data" in training_response
                    ):
                        data = training_response["data"]

                        # Update result artifact_uri with trained model path
                        result_obj = Result.objects.get(
                            id=training_run_update.result.id
                        )
                        result_obj.artifact_uri = data.get("model_path", "")
                        result_obj.accuracy = data.get("accuracy")
                        result_obj.loss = data.get("loss")
                        result_obj.save()

                        logger.info(
                            f"Training completed successfully for TrainingRun ID: {training_run_id}"
                        )
                    else:
                        error_msg = training_response.get("message", "Unknown error")
                        logger.error(
                            f"Training failed for TrainingRun ID: {training_run_id}: {error_msg}"
                        )

                except Exception as e:
                    logger.error(f"Background: Training failed: {e}")

            # Start the background thread
            thread = threading.Thread(target=async_call)
            thread.daemon = True
            thread.start()

            results.append(
                {
                    "status": "success",
                    "type": "training_start",
                    "message": f"Training started for TrainingRun ID: {training_run_id}. Check logs for completion.",
                }
            )

        except (
            Dataset.DoesNotExist,
            ModelVersion.DoesNotExist,
            TrainingRun.DoesNotExist,
        ) as e:
            logger.error(f"Object lookup failed: {e}")
            results.append(
                {
                    "status": "error",
                    "type": "training_start",
                    "message": f"Object lookup failed: {e}",
                }
            )
    else:
        results.append(
            {
                "status": "error",
                "type": "training_start",
                "message": "Invalid request method",
            }
        )

    return render(request, "training_return.html", {"results": results})
