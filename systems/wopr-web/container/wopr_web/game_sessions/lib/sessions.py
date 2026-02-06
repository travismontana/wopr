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

logger = setup_logger()
config = get_config()

def start_session(gsession, request, player_ids):
    max_turns = 3
    max_rounds = 10
   
    number_players = gsession.players.count()
    current_round = Round.objects.filter(session=gsession).order_by('-number').first()
    if not current_round:
        current_round = Round.objects.create(session=gsession, number=1)
        # add logic to add the seats

    sp = SessionPlayer.objects.filter(session=gsession).order_by("seat")
    if sp.count() != number_players:
       # error
       return 1

    turns_in_round = TurnInRound.objects.filter(round=current_round).count()
    if turns_in_round <= max_turns:
        for seat in sp:
            player = seat.player
            logger.info(f"Player {player.handle} is in seat {seat.seat} for session {gsession.short_id}")
            # do cool things.
            # create the turn object

