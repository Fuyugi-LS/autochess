import sys
import subprocess
import os

sys.path.append('d:/work/autochess/chess')
import chessAi
from engine import GameState, Move
from queue import Queue

# Force Maia by monkeypatching randint to always return 1
chessAi.random.randint = lambda a, b: 1
chessAi.initialize_engines()

print(f"Engine chosen: {chessAi.get_current_engine_stats()['name']}")

gs = GameState()
validMoves = gs.getValidMoves()

print("\n--- MAIA MOVE 1 ---")
q = Queue()
chessAi.findBestMove(gs, validMoves, q)
best_move = q.get()
if best_move:
    print(f"Maia Chosen UCI: {best_move.getUCINotation()}")
    gs.makeMove(best_move)
else:
    print("FAILED TO FIND MAIA MOVE")

print("\n--- HUMAN MOVE 1 ---")
# Let's say human plays e5
validMoves = gs.getValidMoves()
e5_move = next((m for m in validMoves if m.getUCINotation() == 'e7e5'), validMoves[0])
print(f"Human Chosen UCI: {e5_move.getUCINotation()}")
gs.makeMove(e5_move)

print("\n--- MAIA MOVE 2 ---")
validMoves = gs.getValidMoves()
q = Queue()
chessAi.findBestMove(gs, validMoves, q)
best_move2 = q.get()
if best_move2:
    print(f"Maia Chosen UCI: {best_move2.getUCINotation()}")
else:
    print("FAILED TO FIND MAIA MOVE")

chessAi.quit_stockfish()
sys.exit(0)
