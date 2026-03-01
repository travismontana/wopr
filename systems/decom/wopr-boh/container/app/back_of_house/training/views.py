import json
import threading

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from core.models import ModelVersion, ModelInfo, TrainingRun, Dataset, Result

from .lib.lib_training import list_all_projects, get_training_uuid
from django.utils.timezone import now
from lib.helpers import setup_logger
from models.lib.lib_model import call_model_ctl  # Single consistent import

logger = setup_logger()


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


def training_detail(request, pk):  # FIXED: Added pk parameter
    """Display details for a specific training run"""
    try:
        training_run = TrainingRun.objects.get(id=pk)
        dataset = training_run.dataset
        result = training_run.result

        needs = []
        if "/dev/null" in dataset.artifact_uri:
            needs.append({"set": "dataset", "needs": "artifact_uri"})
        if "/dev/null" in result.artifact_uri:
            needs.append({"set": "result", "needs": "artifact_uri"})

        logger.info(f"Retrieved details for TrainingRun ID: {pk}")
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
        logger.error(f"TrainingRun {pk} not found")
        messages.error(request, f"Training run {pk} not found")
        return redirect("index")


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

                    dataz = call_model_ctl(payload)  # FIXED: consistent function name
                    logger.info(f"Background: Dataset generation response: {dataz}")

                    dataset_obj = Dataset.objects.get(uuid=dataset_uuid)

                    if dataz.get("status") == "success" and "data" in dataz:
                        data = dataz["data"]

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
                        dataset_obj.note = json.dumps({"error": error_msg})
                        dataset_obj.save()

                except Exception as e:
                    logger.error(f"Background: Dataset generation failed: {e}")
                    try:
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
    """Display training parameter form"""
    logger.info("Training setup requested")
    results = []
    if request.method == "POST":
        logger.info("Processing training setup POST request")
        training_run_id = request.POST.get("training_run_id")
        results.append({"training_run_id": training_run_id})  # For debugging purposes
        dataset_id = request.POST.get("dataset_id")
        results.append({"dataset_id": dataset_id})  # For debugging purposes
        try:
            logger.info("Trying to retrieve training setup details")
            training_run_obj = TrainingRun.objects.get(id=training_run_id)
            results.append({"training_run_obj": str(training_run_obj)})  # Debug
            dataset_obj = Dataset.objects.get(id=dataset_id)
            results.append({"dataset_obj": str(dataset_obj)})  # Debug
            logger.info(
                f"Retrieved TrainingRun ID: {training_run_id}, Dataset ID: {dataset_id}"
            )

            model_id = training_run_obj.model_version.model.id
            results.append({"model_id": model_id})  # Debug
            logger.info(
                f"training_setup - Retrieving ModelVersion for Model ID: {model_id}"
            )
            model_vers = ModelVersion.objects.get(model=model_id)
            results.append({"model_vers": str(model_vers)})  # Debug
            logger.info(
                f"Preparing training setup for Model ID: {model_id}, Dataset ID: {dataset_id}"
            )
            context = {
                "model": model_vers.model,
                "model_ver": model_vers,
                "dataset": dataset_obj,
                "training_run": training_run_obj,
            }
            results.append({"context": str(context)})  # Debug
            logger.debug(f"Training setup context: {context}")
            return render(request, "training_setup.html", context)
        except Exception as e:
            logger.error(f"Training setup failed: {e}")
            results.append({"error": str(e)})  # Debug
            render(request, "training_return.html", {"results": results})
    return render(request, "training_return.html", {"results": results})


def training_results(request):
    """Process training parameters and kick off training"""
    if request.method == "POST":
        logger.info("Processing training results POST request")

        # Extract form data
        dataset_id = request.POST.get("dataset_id")
        model_ver_id = request.POST.get("model_version_id")
        training_run_id = request.POST.get("training_run_id")

        # Get training parameters from form
        epochs = int(request.POST.get("epochs", 100))
        batch_size = int(request.POST.get("batch_size", 16))
        imgsz = int(request.POST.get("imgsz", 640))
        patience = int(request.POST.get("patience", 50))

        logger.info(
            f"Received IDs - Dataset: {dataset_id}, ModelVersion: {model_ver_id}, TrainingRun: {training_run_id}"
        )

        if not all([dataset_id, model_ver_id, training_run_id]):
            logger.error("Missing required IDs")
            messages.error(request, "Missing required fields")
            return redirect("index")

        try:
            # Fetch objects
            dataset_obj = Dataset.objects.get(id=dataset_id)
            model_ver_obj = ModelVersion.objects.get(id=model_ver_id)
            training_run = TrainingRun.objects.get(id=training_run_id)

            # Build training parameters
            training_params = {
                "epochs": epochs,
                "batch_size": batch_size,
                "imgsz": imgsz,
                "patience": patience,
            }

            logger.info(f"Starting training for TrainingRun ID: {training_run.id}")

            # Build callback URL that model_ctl will call when done
            callback_url = request.build_absolute_uri(reverse("training_callback"))

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
                    "id": training_run.id,
                    "uuid": str(training_run.uuid),
                },
                "training_params": training_params,
                "callback_url": callback_url,
            }

            def async_call():
                try:
                    logger.info(
                        f"Background: Starting training for TrainingRun ID: {training_run.id}"
                    )
                    training_response = call_model_ctl(payload)

                    # Just check that training was started
                    if training_response.get("status") == "started":
                        logger.info(
                            f"Training started successfully for run {training_run.id}"
                        )
                        # Results will come via callback - nothing more to do here
                    else:
                        if "already" in training_response.get("message", "").lower():
                            render(
                                request,
                                "training_return.html",
                                {
                                    "status": "in progress",
                                    "type": "training",
                                    "message": f"Training already in progress for run {training_run.id}",
                                },
                            )
                        logger.error(f"Failed to start training: {training_response}")

                except Exception as e:
                    logger.error(f"Background: Training failed to start: {e}")

            thread = threading.Thread(target=async_call)
            thread.daemon = True
            thread.start()

            messages.success(
                request,
                "Training started! Results will update automatically when complete.",
            )
            return redirect("training_detail", pk=training_run.id)

        except (
            Dataset.DoesNotExist,
            ModelVersion.DoesNotExist,
            TrainingRun.DoesNotExist,
        ) as e:
            logger.error(f"Object not found: {e}")
            messages.error(request, "Invalid dataset, model version, or training run")
            return redirect("index")
        except Exception as e:
            logger.error(f"Training start failed: {e}")
            messages.error(request, f"Training start failed: {str(e)}")
            return redirect("index")

    return redirect("index")


@csrf_exempt  # External service calling this
@require_POST
def training_callback(request):
    """
    Callback endpoint for model_ctl to report training completion.
    Called by FastAPI when training finishes (success or failure).
    """
    try:
        # Parse JSON body
        data = json.loads(request.body)

        training_run_id = data.get("training_run_id")
        training_status = data.get("status")
        metrics = data.get("metrics")
        model_path = data.get("model_path")
        error = data.get("error")

        logger.info(
            f"Received training callback for run {training_run_id}: {training_status}"
        )

        if not training_run_id:
            return JsonResponse({"error": "training_run_id required"}, status=400)

        # Get the training run and result
        training_run = TrainingRun.objects.get(id=training_run_id)
        result_obj = training_run.result

        if training_status == "success":
            # Update result with trained model path
            result_obj.artifact_uri = model_path

            # Store metrics in metadata field (assuming JSONField)
            result_obj.metadata = metrics or {}
            result_obj.save()

            logger.info(f"Updated TrainingRun {training_run_id} with results")
            logger.info(f"Metrics: {metrics}")

            return JsonResponse(
                {"status": "updated", "training_run_id": training_run_id}
            )

        elif training_status == "error":
            logger.error(f"Training failed for run {training_run_id}: {error}")
            # Store error info in metadata
            result_obj.metadata = {"error": error, "status": "failed"}
            result_obj.save()

            return JsonResponse(
                {"status": "error_recorded", "training_run_id": training_run_id}
            )

        else:
            logger.warning(
                f"Unknown status '{training_status}' for run {training_run_id}"
            )
            return JsonResponse(
                {"error": f"Unknown status: {training_status}"}, status=400
            )

    except TrainingRun.DoesNotExist:
        logger.error(f"TrainingRun {training_run_id} not found")
        return JsonResponse({"error": "TrainingRun not found"}, status=404)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in callback")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Callback processing failed: {e}")
        return JsonResponse({"error": str(e)}, status=500)
