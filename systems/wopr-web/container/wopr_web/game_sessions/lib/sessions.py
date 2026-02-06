"""

SESSION START
├─ Validate: Session has players with seats assigned
├─ Config: max_rounds=10, max_turns=3 (per round)
└─ Initialize: round_num=1, turn_num=1

MAIN LOOP (HTTP POST-driven state machine)
├─ GET CURRENT STATE
│  ├─ Which round? (1-10)
│  ├─ Which turn in round? (1-3)
│  ├─ Which turn globally? (1-30)
│  └─ Which player's move next? (by seat order)
│
├─ VALIDATE STATE
│  ├─ Check: round_num <= max_rounds
│  ├─ Check: turns_in_round < max_turns
│  ├─ Check: moves_in_turn < player_count
│  └─ If any boundary hit → advance state or end session
│
├─ EXECUTE MOVE
│  ├─ Get next player (ordered by SessionPlayer.seat)
│  ├─ Capture image → grab_capture(payload)
│  ├─ Create Image record
│  ├─ Create Move(player, turn, image)
│  └─ Log move completion
│
└─ ADVANCE STATE
   ├─ moves_in_turn++
   ├─ IF moves_in_turn == player_count:
   │  ├─ Turn complete
   │  ├─ turns_in_round++
   │  ├─ IF turns_in_round == max_turns:
   │  │  ├─ Round complete
   │  │  ├─ round_num++
   │  │  ├─ IF round_num > max_rounds:
   │  │  │  └─ SESSION COMPLETE
   │  │  └─ ELSE:
   │  │     ├─ Create Round(session, round_num)
   │  │     └─ Create Turn(session, round, global_turn_num++)
   │  └─ ELSE:
   │     └─ Create Turn(session, round, global_turn_num++)
   └─ Return current state for display

Each Session has players  (SessionPlayers)
10 Rounds each round is
3 Turns each turn is
1 Move from Each Player in seat order (SessionPlayer.seat)

"""

from django.shortcuts import render, redirect
from lib.helpers import get_config, setup_logger
import json
import uuid
from pathlib import Path
from game_sessions.forms import (
    GameForm,
    GameSessionForm,
    PlayerForm,
    SessionPlayerForm,
    SessionImageForm,
)

from core.models import Game, Session, SessionPlayer, Player, SessionImage, Image, Round, Turn, Move

from game_sessions.lib.captures import grab_capture

logger = setup_logger()
config = get_config()


def get_session_state(session):
    """
    Returns current session state without modifying anything.
    """
    # Get current round (latest by number)
    current_round = Round.objects.filter(session=session).order_by("-number").first()

    # Get current turn (latest by number)
    current_turn = Turn.objects.filter(session=session).order_by("-number").first()

    # Count moves in current turn
    moves_in_turn = (
        Move.objects.filter(turn=current_turn).count() if current_turn else 0
    )

    # Count turns in current round
    turns_in_round = (
        Turn.objects.filter(round=current_round).count() if current_round else 0
    )

    # Get player count
    player_count = session.sessionplayer_set.count()

    # Get next player (if turn not complete)
    next_player = get_next_player(session, current_turn, moves_in_turn)

    return {
        "round_num": current_round.number if current_round else 0,
        "turn_num": current_turn.number if current_turn else 0,
        "turns_in_round": turns_in_round,
        "moves_in_turn": moves_in_turn,
        "player_count": player_count,
        "next_player": next_player,
        "is_complete": False,
        # "is_complete": check_if_complete(current_round, turns_in_round),
    }


def get_next_player(session, current_turn, moves_in_turn):
    """
    Returns the next player to move based on seat order.
    """
    # Get players ordered by seat
    session_players = session.sessionplayer_set.order_by("seat")

    # Get players who have already moved this turn
    if current_turn:
        moved_player_ids = Move.objects.filter(turn=current_turn).values_list(
            "player_id", flat=True
        )

        # Get next player who hasn't moved
        for sp in session_players:
            if sp.player_id not in moved_player_ids:
                return sp.player
    else:
        # First move of session, return lowest seat
        return session_players.first().player

    return None  # Turn is complete


def advance_session(session, note=""):
    """
    Execute one move and advance state.
    Returns updated state.
    """
    MAX_ROUNDS = 10
    MAX_TURNS = 3

    state = get_session_state(session)

    # Check if session complete
    if state["round_num"] >= MAX_ROUNDS and state["turns_in_round"] >= MAX_TURNS:
        return {"status": "complete"}

    # INITIALIZATION: If no rounds exist, create Round 1 & Turn 1 but DON'T capture yet
    if state["round_num"] == 0:
        current_round = Round.objects.create(session=session, number=1)
        current_turn = Turn.objects.create(
            session=session, round=current_round, number=1, note=note
        )
        return {
            "status": "initialized",
            "state": get_session_state(session),
        }

    # Get current round and turn
    current_round = Round.objects.get(session=session, number=state["round_num"])
    current_turn = Turn.objects.get(session=session, number=state["turn_num"])

    # Save note to CURRENT turn (the one being played)
    if note:
        current_turn.note = note
        current_turn.save()

    # Execute move for next player
    next_player = state["next_player"]

    if not next_player:
        # Turn is complete, need to create next turn/round
        state["turns_in_round"] += 1

        # Check if round complete
        if state["turns_in_round"] >= MAX_TURNS:
            state["round_num"] += 1

            if state["round_num"] > MAX_ROUNDS:
                return {"status": "complete"}

            # Create next round
            current_round = Round.objects.create(
                session=session, number=state["round_num"]
            )
            state["turns_in_round"] = 0

        # Create next turn (without note - that'll come on next POST)
        state["turn_num"] += 1
        current_turn = Turn.objects.create(
            session=session, round=current_round, number=state["turn_num"]
        )

        # Return WITHOUT capturing - next click will capture first move
        return {
            "status": "turn_created",
            "state": get_session_state(session),
        }

    # Capture image and create move
    image = capture_and_create_image()
    move = Move.objects.create(
        player=next_player, turn=current_turn, image_at_end=image
    )

    logger.info(f"Created move for {next_player.handle} in turn {current_turn.number}")

    return {"status": "active", "state": get_session_state(session)}


def capture_and_create_image():
    """
    Captures an image and creates a SessionImage linked to the session.
    """
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
    results = grab_capture(payload)
    if results is None:
        logger.error("Failed to capture image")
        return None

    data = json.loads(results)
    extra = data.get("extra", {})
    filepath = extra.get("filepath")
    checksum = extra.get("checksum")

    imageinfo = Image.objects.create(
        filename=filename, artifact_uri=filepath, checksum=checksum
    )
    return imageinfo
