import os, sys
sys.path.append('d:/work/autochess/chess')
from engine import GameState, Move
from chessAi import initialize_engines, findBestMove, get_current_engine_stats, MAIA_PROCESS, STOCKFISH_PROCESS
import random
from queue import Queue
import time

random.seed(42) # Let's see what engine it picks
initialize_engines()
print(f"Engine chosen: {get_current_engine_stats()['name']}")

gs = GameState()
validMoves = gs.getValidMoves()

print("\n--- WHITE MOVE ---")
q = Queue()
findBestMove(gs, validMoves, q)
best_move = q.get()
print(f"White Best Move object: {best_move}")
if best_move:
    print(f"White Chosen UCI: {best_move.getUCINotation()}")
    gs.makeMove(best_move)
else:
    print("FAILED TO FIND WHITE MOVE")
    
validMoves = gs.getValidMoves()

print("\n--- BLACK MOVE ---")
q = Queue()
findBestMove(gs, validMoves, q)
best_move_black = q.get()
print(f"Black Best Move object: {best_move_black}")
if best_move_black:
    print(f"Black Chosen UCI: {best_move_black.getUCINotation()}")
else:
    print("FAILED TO FIND BLACK MOVE")
    
sys.exit(0)
