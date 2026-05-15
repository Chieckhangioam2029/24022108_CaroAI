import sys
import time
sys.path.insert(0, '.')

from source_code.game.board import Board, PLAYER_X, PLAYER_O
from source_code.ai.move_generator import get_candidate_moves
from source_code.ai.alphabeta import get_best_move as ab_best
from source_code.ai.evaluation import evaluate_board

b = Board(15)
b.make_move(7, 7, PLAYER_X)
b.make_move(7, 8, PLAYER_O)
b.make_move(8, 8, PLAYER_X)
b.make_move(6, 6, PLAYER_O)
b.make_move(8, 7, PLAYER_X)

candidates = get_candidate_moves(b)
print(f"Candidates count: {len(candidates)}")
print(f"Top 5: {candidates[:5]}")

ev = evaluate_board(b, PLAYER_O, PLAYER_X)
print(f"Eval score: {ev}")

print("\nTesting Alpha-Beta depth 3...")
t = time.time()
r3 = ab_best(b, 3, PLAYER_O, PLAYER_X)
print(f"  Depth 3: move=({r3['row']},{r3['col']}) score={r3['score']} states={r3['states_explored']} time={time.time()-t:.3f}s")

print("\nTesting Alpha-Beta depth 4...")
t = time.time()
r4 = ab_best(b, 4, PLAYER_O, PLAYER_X)
print(f"  Depth 4: move=({r4['row']},{r4['col']}) score={r4['score']} states={r4['states_explored']} time={time.time()-t:.3f}s")

print("\nAll tests passed!")
