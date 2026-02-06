from django.shortcuts import render, redirect
from pathlib import Path
import json
import uuid
from .forms import (
    GameForm,
    GameSessionForm,
    PlayerForm,
    SessionPlayerForm,
    SessionImageForm,
)

from core.models import Game, Session, SessionPlayer, Player, SessionImage, Image

from .lib.captures import grab_preview, grab_capture
from .lib.sessions import (
    get_session_state,
    get_next_player,
    advance_session,
)

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
    rounds = Round.objects.filter(session=session_id).order_by("number")
    for round in rounds:
        turns = Turn.objects.filter(round=round).order_by("number")
        for turn in turns:
            moves = Move.objects.filter(turn=turn).select_related(
                "image_at_end", "player"
            )
    url = f"{config['api']['images_url']}"
    thumb_url = f"{config['api']['thumbs_url']}/insecure/resize:fill:300:200/plain/{config['api']['images_url']}"
    context = {
        "gsession": gsession,
        "form": form,
        "session_images": gsession.sessionimage_set.all(),
        "imgurl": url,
        "thumburl": thumb_url,
        "moves": moves,
    }
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
        context["gsession_id"] = gsession_id
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
        has_sword = request.POST.get("has_sword")
        if "yes" in has_sword.lower():
            # filename: gsession[uuid].jpg
            # path: configbas/{image_dir}/filename
            uuidname = str(uuid.uuid4())
            filename = f"{uuidname}.jpg"
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
                data = json.loads(
                    grab_capture_results
                )  # or grab_capture_results.json() if it's a requests.Response
                extra = data.get("extra", {})
                filepath = extra.get("filepath")
                checksum = extra.get("checksum")

                imageinfo = Image.objects.create(
                    filename=filename, artifact_uri=filepath, checksum=checksum
                )

                SessionImage.objects.create(session=gsession, image=imageinfo)

                logger.info(
                    f"Created image {imageinfo.short_id} for session {gsession.short_id}"
                )
                return redirect("gs_view_specific", session_id=gsession.id)
        else:
            return render(request, "take_capture.html", context)
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


def run_session(request):
    """
    Display session runner interface. 
    POST with 'action=advance' to execute a move.
    """
    if request.method == "POST":
        session_id = request.POST.get("gsession_id")

        if not session_id:
            return render(
                request,
                "gs_results.html",
                {
                    "results": [
                        {
                            "status": "error",
                            "message": "No session ID provided.",
                            "extra": [],
                        }
                    ]
                },
            )

        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            results = [
                {
                    "status": "error",
                    "message": f"Session with ID {session_id} does not exist.",
                    "extra": [],
                }
            ]
            return render(request, "gs_results.html", {"results": results})

        # Only advance if explicitly requested
        action = request.POST.get("action")
        if action == "advance":
            note = request.POST.get("note", "")  # Get note from textarea
            result = advance_session(session, note)  # Fixed: removed extra 's'

            if result["status"] == "complete":
                context = {"message": "Session complete!", "session": session}
                return render(request, "gs_complete.html", context)

        # Always show current state
        state = get_session_state(session)
        context = {
            "session": session,
            "state": state,
            "round_num": state["round_num"],
            "turn_num": state["turn_num"],
            "next_player": state["next_player"],
        }
        return render(request, "gs_session.html", context)

    return redirect("gs_index")
