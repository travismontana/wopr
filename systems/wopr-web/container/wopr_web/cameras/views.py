from django.shortcuts import render
import json
import uuid
import requests
from pathlib import Path
from lib.helpers import get_config, setup_logger
from django.http import StreamingHttpResponse

logger = setup_logger()
config = get_config()

# Create your views here.
def cameras_index(request):
    context = {}
    return render(request, "cameras_still_stream.html", context)


def c950_stream(request):
    context = {}
    c950_host = config["camera"]["camDict"]["2"]["host"]
    c950_port = config["camera"]["camDict"]["2"]["port"]
    c950_url = f"http://{c950_host}:{c950_port}/stream"
    c950_stream = requests.get(c950_url, stream=True)
    context["c950_stream"] = StreamingHttpResponse(
        c950_stream.raw,
        content_type="multipart/x-mixed-replace; boundary=frame",
    )
    return render(request, "cameras_still_stream.html", context)


def c960_stream(request):
    context = {}
    c960_host = config["camera"]["camDict"]["1"]["host"]
    c960_port = config["camera"]["camDict"]["1"]["port"]
    c960_url = f"http://{c960_host}:{c960_port}/stream"
    c960_stream = requests.get(c960_url, stream=True)
    context["c960_stream"] = StreamingHttpResponse(
        c960_stream.raw,
        content_type="multipart/x-mixed-replace; boundary=frame",
    )
    return render(request, "cameras_still_stream.html", context)


def grab_snapshot(request):
    context = {}
    if request.method == "POST":
        camera = request.POST.get("camera")
        cam_host = config["camera"]["camDict"][str(camera)]["host"]
        cam_port = config["camera"]["camDict"][str(camera)]["port"]
        camera_url = f"http://{cam_host}:{cam_port}/snapshot"

        resp = requests.get(camera_url)
        resp.raise_for_status()

        uuidname = str(uuid.uuid4())
        filename = f"{uuidname}.jpg"

        base = config["storage"]["base_path"]
        images = config["storage"]["images_subdir"]
        incoming = config["storage"]["incoming_subdir"]
        path = Path(base) / images / incoming / filename
        filepath = str(path)

        with open(filepath, "wb") as f:
            f.write(resp.content)

        logger.info(f"Saved snapshot to {filepath}")
        return render(request, "cameras_still_stream.html", context)
