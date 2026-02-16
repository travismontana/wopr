#!/usr/bin/env python3

import logging

import jpype
import jpype.imports


logger = logging.getLogger(__name__)
# add stdout to the mix
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

logger.info("Starting JVM...")
logger.info(f"Default JVM Path: {jpype.getDefaultJVMPath()}")
jpype.startJVM(classpath=["./Ludii.jar"])
logger.info("JVM started.")


from other.context import Context
from other.trial import Trial
from other import GameLoader
from java.io import File
from java.util import ArrayList, List
from utils import RandomAI

# Load a game
logger.info("Loading game: dejarik.lud")
game = GameLoader.loadGameFromFile(File("dejarik.lud"))
logger.info(f"Game: {game}")
trial = Trial(game)
context = Context(game, trial)

# Query legal moves
# moves = game.moves(context).moves()
# logger.info(f"Legal moves: {moves.size()}")

num_trials = 5
ais = ArrayList()
ais.add(None)
for p in range(1, game.players().count() + 1):
    ais.add(RandomAI())

for i in range (num_trials):
    game.start(context)
    for p in range(1, game.players().count() + 1):
        ais.get(p).initAI(game, p)
    
    model = context.model()
    
    while (trial.over() == False):
        model.startNewStep(context,ais,1.0)
    
    ranking = trial.ranking()
    for p in range(1, game.players().count() + 1):
        logger.info(f"Player {p} ranking: {ranking[p]}")
        print(f"Player {p} ranking: {ranking[p]}")