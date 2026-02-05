from django.shortcuts import render, redirect
from pathlib import Path
from .forms import (
    GameForm,
    GameSessionForm,
    PlayerForm,
    SessionPlayerForm,
    SessionImageForm,
)

from core.models import Game, Session, SessionPlayer, Player, SessionImage, Image

from .lib.captures import grab_preview, grab_capture

from lib.helpers import get_config, setup_logger

logger = setup_logger()
config = get_config()

# Create your views here.
def gs_index(request):
    context = {}
    return render(request, "gs_index.html", context)


def gs_new_form(request):
    context = {}
    if request.method == "POST":
        form = GameSessionForm(request.POST)
        if form.is_valid():
            # Process the form data here
            form.save()
            return redirect("gs_existing")
    else:
        form = GameSessionForm()
    context["form"] = form
    return render(request, "gs_new.html", context)


def game_new_form(request):
    context = {}
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            # Process the form data here
            form.save()
            return redirect("gs_new")
    else:
        form = GameForm()
    context["form"] = form
    return render(request, "game_new.html", context)


def gs_existing(request):
    existing = Session.objects.all()
    context = {"gs_list": existing}
    return render(request, "gs_existing.html", context)


def gs_view_specific(request, session_id):
    gsession = Session.objects.get(id=session_id)

    if request.method == "POST":
        form = SessionPlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("gs_view_specific", session_id=session_id)
    else:
        form = SessionPlayerForm(initial={"session": gsession})

    context = {"gsession": gsession, "form": form}
    return render(request, "gs_view_specific.html", context)


def game_view_specific(request, game_id):
    context = {"game_id": game_id}
    return render(request, "game_view_specific.html", context)


def game_list(request):
    context = {}
    games = Game.objects.all()
    context["games"] = games
    return render(request, "game_list.html", context)


def player_new_form(request):
    context = {}
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            # Process the form data here
            form.save()
            return redirect("player_list")
    else:
        form = PlayerForm()
    context["form"] = form
    return render(request, "player_new.html", context)


def player_list(request):
    context = {}
    players = Player.objects.all()
    context["players"] = players
    return render(request, "player_list.html", context)


def player_view_specific(request, player_id):
    context = {"player_id": player_id}
    return render(request, "player_view_specific.html", context)


def add_player_to_session(request, session_id):
    session = Session.objects.get(id=session_id)

    if request.method == "POST":
        form = SessionPlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("gs_view_specific", session_id=session.id)
    else:
        form = SessionPlayerForm(initial={"session": session})

    context = {"form": form, "gsession": session}
    return render(request, "add_player_to_session.html", context)


def take_captures(request):
    context = {}

    if request.method == "POST":
        gsession_id = request.POST.get("gsession_id")
        try:
            gsession = Session.objects.get(id=gsession_id)
        except Session.DoesNotExist:
            results = [
                {
                    "status": "error",
                    "message": f"Session with ID {gsession_id} does not exist.",
                    "extra": [],
                }
            ]
            return render(request, "gs_results.html", {"results": results})
        context["gsession"] = gsession
        # filename: gsession[uuid].jpg
        # path: configbas/{image_dir}/filename

        filename = f"{gsession.uuid}.jpg"
        base = config["storage"]["base_path"]
        images = config["storage"]["images_subdir"]
        incoming = config["storage"]["incoming_subdir"]
        path = Path(base) / images / incoming / filename
        filepath = str(path)

        width = config["camera"]["camDict"]["0"]["width"]
        height = config["camera"]["camDict"]["0"]["height"]

        payload = {
            "filepath": filepath,
            "width": width,
            "height": height,
        }
        grab_capture_results = grab_capture(payload)
        logger.info(f"Grab capture results: {grab_capture_results}")
        if grab_capture_results is not None:
            context["capture_results"] = grab_capture_results
            data = grab_capture_results.json()
            filepath = data.get("filepath", None)
            checksum = data.get("checksum", None)
            imageform = ImageForm(
                initial={
                    "artifact_uri": filepath,
                    "checksum": checksum,
                    "filename": filename,
                }
            )
            imageinfo = Image(
                filename=filename, artifact_uri=filepath, checksum=checksum
            )
            imageform.save()
            sessionimageform = SessionImageForm(
                initial={
                    "session": gsession,
                    "image": imageinfo,
                }
            )
            if sessionimageform.is_valid():
                sessionimageform.save()
        else:
            results = [
                {
                    "status": "error",
                    "message": "Failed to fetch capture preview.",
                    "extra": [],
                }
            ]
            context["results"] = results
            return render(request, "gs_results.html", context)
    else:
        context = {"error": "No session ID provided."}
    return render(request, "take_capture.html", context)


def capture_preview(request):
    context = {}

    if request.method == "POST":
        gsession_id = request.POST.get("gsession_id")
        gsession = Session.objects.get(id=gsession_id)
        context["gsession"] = gsession

        grab_preview_results = grab_preview()
        if grab_preview_results is not None:
            context["preview_results"] = grab_preview_results
        else:
            results = [
                {
                    "status": "error",
                    "message": "Failed to fetch capture preview.",
                    "extra": [],
                }
            ]
            context["results"] = results
            return render(request, "gs_results.html", context)
    else:
        context = {"error": "No session ID provided."}
        return render(request, "gs_results.html", context)

    return render(request, "take_capture.html", context)


def capture_results(request):
    context = {}

    if request.method == "POST":
        gsession_id = request.POST.get("gsession_id")
        gsession = Session.objects.get(id=gsession_id)
        context["gsession"] = gsession

        return render(request, "gs_results.html", context)

    return render(request, "gs_results.html", context)
