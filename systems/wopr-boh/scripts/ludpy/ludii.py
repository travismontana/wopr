#!/usr/bin/env python3
import os
import logging
import argparse
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


"""
map_cells
"""


def map_cells(game):
    """
    Creates a dict of the cell mappings for the given game.
    Args:
        game (_type_): _description_
    Returns:
        dict: A dictionary mapping cell identifiers to their corresponding positions.
    """
    logger.info("Mapping cells for game: %s", game.getName())

    topo = game.board().topology()
    logger.info("Topology for game: %s", len(topo))
    logger.debug("Topology details: %s", topo)
    cell_mapping = {}

    cells = topo.cells()
    logger.info("Number of cells: %s", len(cells))
    logger.debug("Cell details: %s", cells)

    for site in range(cells.size()):
        label = None
        label = cells.get(site).label()
        logger.info("Site: %s", site)
        logger.info("Mapping cell: %s", label)
        if label is not None:
            cell_mapping[str(label)] = site
            logger.info("Mapped cell: %s to site: %s", label, site)
    logger.info("Completed mapping cells for game: %s", game.getName())
    logger.debug("Cell mapping details: %s", cell_mapping)
    return cell_mapping


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

if args.info:
    logger.info(f"Game information: {game}")
    print(f"Game information:    {game}")
    print(f"Trial information:   {trial}")
    print(f"Context information: {context}")

if args.moves:
    logger.info(f"Moves file specified: {args.moves}")
    moves_file = args.moves
    if not os.path.isfile(moves_file):
        logger.error(f"Moves file does not exist: {moves_file}")
        exit(1)
    else:
        logger.info(f"Moves file exists: {moves_file}")
    # playerid or name
    #

print("sync;sync")
exit(0)
