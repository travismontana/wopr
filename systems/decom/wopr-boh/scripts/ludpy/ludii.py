#!/usr/bin/env python3
import os
import csv
import logging
import argparse
import textwrap
import shutil
import jpype
import jpype.imports
print("start")


def setup_logger():
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler("ludii.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)20s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = setup_logger()
logger.debug("Starting JVM...")
logger.debug(f"Default JVM Path: {jpype.getDefaultJVMPath()}")
jpype.startJVM(
    "-Djava.awt.headless=true",
    "--enable-native-access=ALL-UNNAMED",
    classpath=["./Ludii.jar"],
)
logger.debug("JVM started.")

from other.context import Context
from other.trial import Trial
from other import GameLoader
from java.io import File
from java.util import ArrayList, List
from utils import RandomAI


def map_pieces(game):
    pieces = game.equipment().components()
    piece_mapping = {}
    for piece in pieces:
        name = piece.name()
        if name is not None:
            piece_mapping[str(name)] = piece
    return piece_mapping


# Setup the argparser
def setup_arg():
    parser = argparse.ArgumentParser(description="Ludii Game Runner")
    parser.add_argument(
        "--game",
        type=str,
        default="files/dejarik.lud",
        help="Path to the Ludii game file",
    )
    parser.add_argument(
        "--moves",
        type=str,
        default="file/moves.csv",
        help="Path to the moves file",
    )
    parser.add_argument(
        "-i", "--info", action="store_true", help="Display game information"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    return parser


# do_move
def do_moves(moves_file, game, trial, context):
    results = []
    logger.info(f"Processing moves from file: {moves_file}")
    model = context.model()
    piece_maps = map_pieces(game)
    ais = ArrayList()
    ais.add(None)
    rows = []
    for p in range(1, game.players().count() + 1):
        ai = RandomAI()
        ai.initAI(game, p)
        ais.add(ai)
    with open(moves_file, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            rows.append(row)
        logger.info(f"Total lines read: {len(rows)}")
    logger.debug(f"Rows details: {rows}")
    logger.info(f"Fields: {', '.join(fields)}")
    first_run = True
    for move in rows:
        this_move_results = []
        logger.info(f"Working on: {move}")
        # playerid,pieceid,destcell
        player_id = move[0]
        piece_id = move[1]
        source_cell = int(move[2])
        source_cell_validated = source_cell if 0 < source_cell < 24 else None
        if source_cell_validated is None:
            logger.error(f"Invalid source cell: {source_cell}")
            results.append(
                {
                    "piece_id": piece_id,
                    "source_cell": source_cell,
                    "dest_cell": dest_cell,
                    "move": move,
                    "reason": "Invalid source cell",
                    "status": "illegal",
                    "details": {},
                }
            )
            return results
        logger.info(f"Validated source cell: {source_cell} -> {source_cell_validated}")
        dest_cell = int(move[3])
        dest_cell_validated = dest_cell if 0 < dest_cell < 24 else None
        if dest_cell_validated is None:
            logger.error(f"Invalid destination cell: {dest_cell}")
            results.append(
                {
                    "piece_id": piece_id,
                    "source_cell": source_cell,
                    "dest_cell": dest_cell,
                    "move": move,
                    "reason": "Invalid destination cell",
                    "status": "illegal",
                    "details": {},
                }
            )
            return results
        logger.info(f"Validated destination cell: {dest_cell} -> {dest_cell_validated}")

        piece_id_validated = piece_maps.get(piece_id)
        if piece_id_validated is None:
            logger.error(f"Invalid piece ID: {piece_id}")
            continue
        logger.info(f"Validated piece ID: {piece_id} -> {piece_id_validated}")

        legal_moves = game.moves(context).moves()
        possible_start = []
        possible_dest = []
        for index in range(legal_moves.size()):
            move = legal_moves.get(index)
            possible_start.append(move.fromNonDecision())
            possible_dest.append(move.toNonDecision())
            logger.info(f"Move: {move}")
            if (
                move.fromNonDecision() == source_cell_validated
                and move.toNonDecision() == dest_cell_validated
            ):
                logger.info(f"Found matching move: {move}")
                results.append(
                    {
                        "piece_id": piece_id,
                        "source_cell": source_cell_validated,
                        "dest_cell": dest_cell_validated,
                        "move": move,
                        "reason": "Move matches source and destination cells",
                        "status": "valid",
                        "details": {},
                    }
                )
                continue
        logger.info(f"Results: {results}")
        if len(this_move_results) == 0 and not first_run:
            if source_cell_validated not in possible_start:
                reason = "Source cell is not a possible start"
            elif dest_cell_validated not in possible_dest:
                reason = "Destination cell is not a possible destination"
            else:
                reason = "Move does not match source and destination cells, illegal"
            results.append(
                {
                    "piece_id": piece_id,
                    "source_cell": source_cell_validated,
                    "dest_cell": dest_cell_validated,
                    "move": None,
                    "reason": reason,
                    "status": "illegal",
                    "details": {
                        "possible_start": possible_start,
                        "possible_dest": possible_dest,
                    },
                }
            )
            return results
        else:
            first_run = False
    return results


def print_all(game, trial, context):
    print_info("Game information", game)
    print_info("Player information", game.players())
    print_info("Number of players", game.players().count())
    print_info("Trial information", trial)
    print_info("Context information", context)
    print_info("Board Topology", game.board().topology())
    print_info("Board Topology Details", game.board().topology().cells())
    # inspect(game.board().topology().cells())
    print_info("Cell 0 Details", game.board().topology().cells().get(0).label())
    # inspect(game.board().topology().cells().get(0))
    print_info("Legal Moves", game.moves(context).moves())
    # inspect(game.moves(context).moves())
    print_info("Move 1", game.moves(context).moves().get(1))
    inspect(game.moves(context).moves().get(0))
    print_info(
        "Move 1 toNonDecision()", game.moves(context).moves().get(1).toNonDecision()
    )
    print_info("Pieces info", game.equipment().components())
    for piece in game.equipment().components():
        print_info(f"Piece {piece.name()}", piece)
        inspect(piece)
    print_info("Pieces info", game.equipment().components())
    # inspect(game.equipment().components().name())

    print_info_flush()


def print_info(label, value):
    """Print a label/value pair, aligned and word-wrapped."""
    print_info.entries.append((label, str(value)))


print_info.entries = []


def print_info_flush():
    """Flush all queued entries as aligned columns."""
    if not print_info.entries:
        return

    term_width = shutil.get_terminal_size((100, 40)).columns
    label_width = max(len(e[0]) for e in print_info.entries)
    val_width = max(30, term_width - label_width - 5)

    for label, value in print_info.entries:
        wrapped = textwrap.wrap(value, width=val_width) or [value]
        print(f"  {label:<{label_width}}  {wrapped[0]}")
        for line in wrapped[1:]:
            print(f"  {'':<{label_width}}  {line}")

    print_info.entries = []


def inspect(obj, show_inherited=False):
    """Print all public methods on a JPype-wrapped Java object, aligned."""
    clazz = obj.getClass()
    term_width = shutil.get_terminal_size((100, 40)).columns

    methods = clazz.getMethods() if show_inherited else clazz.getDeclaredMethods()

    entries = []
    for method in methods:
        ret = str(method.getReturnType().getSimpleName())
        name = str(method.getName())
        params = ", ".join(str(p.getSimpleName()) for p in method.getParameterTypes())
        entries.append((ret, f"{name}({params})"))

    entries.sort(key=lambda e: e[1].lower())

    ret_width = max(len(e[0]) for e in entries)
    sig_width = max(30, term_width - ret_width - 6)

    print(f"\n  Class: {clazz.getName()}")
    print(f"  {'─' * (term_width - 4)}")

    for ret, sig in entries:
        wrapped = textwrap.wrap(sig, width=sig_width) or [sig]
        print(f"  {ret:<{ret_width}}  {wrapped[0]}")
        for line in wrapped[1:]:
            print(f"  {'':<{ret_width}}    {line}")

    print(f"  ({len(entries)} methods)\n")


def results_print(results):
    for result in results:
        print(f"** Move Results: **")
        print(f"Piece: {result.get('piece_id')}")
        print(f"Source: {result.get('source_cell')}")
        print(f"Destination: {result.get('dest_cell')}")
        print(f"Move: {result.get('move')}")
        print(f"Status: {result.get('status')}")
        print(f"Reason: {result.get('reason')}")
        for deet in result.get("details", {}):
            print(f"  {deet}: {result['details'][deet]}")
        print()


args = setup_arg().parse_args()

if args.verbose:
    logger.setLevel(logging.DEBUG)
    sto_handler = logging.StreamHandler()
    sto_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)20s - %(message)s"
    )
    sto_handler.setFormatter(formatter)
    logger.addHandler(sto_handler)

if args.game:
    game_file = args.game
    logger.info(f"Game file specified: {game_file}")

    # verify it's a real openable file, then move on.
    if not os.path.isfile(game_file):
        logger.error(f"Game file does not exist: {game_file}")
        exit(1)
    else:
        logger.info(f"Game file exists: {game_file}")

# Load the game
logger.info(f"Loading game: {game_file}")
game = GameLoader.loadGameFromFile(File(game_file))
logger.info(f"Game: {game}")
trial = Trial(game)
logger.info(f"Trial id: {trial}")
context = Context(game, trial)
logger.info(f"Context: {context}")
game.start(context)
if args.info:
    print_all(game, trial, context)

if args.moves:
    logger.info(f"Moves file specified: {args.moves}")
    moves_file = args.moves
    if not os.path.isfile(moves_file):
        logger.error(f"Moves file does not exist: {moves_file}")
        exit(1)
    else:
        logger.info(f"Moves file exists: {moves_file}")
    results = do_moves(moves_file, game, trial, context)
    results_print(results)


if args.info:
    print_all(game, trial, context)

print("sync;sync")
exit(0)
