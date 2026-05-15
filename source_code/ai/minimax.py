import time
import math
import random

from source_code.game.rules import is_terminal
from source_code.ai.evaluation import evaluate_board
from source_code.ai.move_generator import (
    get_candidate_moves, find_winning_moves, find_blocking_moves,
)
from source_code.game.board import PLAYER_X, PLAYER_O


# ================================================================
#  Khối 2: Constants
# ================================================================

WIN_SCORE  = 1_000_000
LOSE_SCORE = -1_000_000
DRAW_SCORE = 0


# ================================================================
#  Khối 3: Terminal evaluation
# ================================================================

def _get_terminal_score(winner, ai_player, human_player, depth):
    if winner == ai_player:
        return WIN_SCORE + depth
    if winner == human_player:
        return LOSE_SCORE - depth
    return DRAW_SCORE


# ================================================================
#  Khối 4: Recursive minimax
#  Issue #12: uses same evaluation, move ordering, candidate
#  generation as alphabeta for fair comparison.
# ================================================================

def minimax(board, depth, maximizing_player, ai_player, human_player, stats):
    stats["states_explored"] += 1

    is_over, winner = is_terminal(board)
    if is_over:
        return _get_terminal_score(winner, ai_player, human_player, depth)

    if depth == 0:
        return evaluate_board(board, ai_player, human_player)

    # Issue #12: pass correct player info for consistent move ordering
    if maximizing_player:
        current_player = ai_player
        opp = human_player
    else:
        current_player = human_player
        opp = ai_player

    candidates = get_candidate_moves(board, current_player, opp)

    if not candidates:
        return evaluate_board(board, ai_player, human_player)

    if maximizing_player:
        best_score = -math.inf
        for row, col in candidates:
            board.make_move(row, col, ai_player)
            score = minimax(board, depth - 1, False, ai_player, human_player, stats)
            board.undo_move()
            best_score = max(best_score, score)
        return best_score

    else:
        best_score = math.inf
        for row, col in candidates:
            board.make_move(row, col, human_player)
            score = minimax(board, depth - 1, True, ai_player, human_player, stats)
            board.undo_move()
            best_score = min(best_score, score)
        return best_score


# ================================================================
#  Khối 5: Top-level get_best_move
#  Issue #12: same tactical layer as alphabeta.
#  Issue #13: benchmark_mode for deterministic results.
# ================================================================

def get_best_move(board, depth, ai_player, human_player, benchmark_mode=False):
    """
    Same structure as alphabeta.get_best_move for fair Level 3 comparison.
    """
    stats = {"states_explored": 0}
    start_time = time.time()

    if len(board.move_history) == 0:
        center = board.size // 2
        elapsed = time.time() - start_time
        return {
            "row": center,
            "col": center,
            "score": 0,
            "states_explored": 0,
            "elapsed_time": elapsed,
            "depth": depth,
            "algorithm": "minimax",
        }

    # --- Tactical layer (same as alphabeta) ---
    # 1. Winning move? Return immediately.
    winning = find_winning_moves(board, ai_player)
    if winning:
        move = winning[0]
        elapsed = time.time() - start_time
        return {
            "row": move[0],
            "col": move[1],
            "score": WIN_SCORE,
            "states_explored": 0,
            "elapsed_time": elapsed,
            "depth": depth,
            "algorithm": "minimax",
        }

    # 2. Must block opponent win? Return blocking move.
    blocking = find_blocking_moves(board, ai_player, human_player)
    if blocking:
        move = blocking[0]
        elapsed = time.time() - start_time
        return {
            "row": move[0],
            "col": move[1],
            "score": WIN_SCORE - 1,
            "states_explored": 0,
            "elapsed_time": elapsed,
            "depth": depth,
            "algorithm": "minimax",
        }

    # --- Normal search ---
    candidates = get_candidate_moves(board, ai_player, human_player)
    best_moves = []
    best_score = -math.inf

    for row, col in candidates:
        board.make_move(row, col, ai_player)
        score = minimax(board, depth - 1, False, ai_player, human_player, stats)
        board.undo_move()

        if score > best_score:
            best_score = score
            best_moves = [(row, col)]
        elif score == best_score:
            best_moves.append((row, col))

    # Issue #13: deterministic in benchmark mode
    if benchmark_mode:
        best_move = best_moves[0]
    else:
        best_move = random.choice(best_moves)

    elapsed = time.time() - start_time

    return {
        "row": best_move[0] if best_move else None,
        "col": best_move[1] if best_move else None,
        "score": best_score,
        "states_explored": stats["states_explored"],
        "elapsed_time": elapsed,
        "depth": depth,
        "algorithm": "minimax",
    }
