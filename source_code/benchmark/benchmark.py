

import sys
import os
import csv
import copy
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from source_code.game.board import PLAYER_X, PLAYER_O
from source_code.ai.minimax import get_best_move as minimax_get_best_move
from source_code.ai.alphabeta import get_best_move as alphabeta_get_best_move
from source_code.benchmark.test_states import TEST_STATES




DEPTHS = [1, 2, 3]
AI_PLAYER = PLAYER_O
HUMAN_PLAYER = PLAYER_X

CSV_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "results.csv")




def run_single(algorithm_name, get_best_move_fn, board, depth):
    test_board = copy.deepcopy(board)

    result = get_best_move_fn(test_board, depth, AI_PLAYER, HUMAN_PLAYER)

    return {
        "algorithm":       algorithm_name,
        "depth":           depth,
        "move":            (result["row"], result["col"]),
        "score":           result["score"],
        "states_explored": result["states_explored"],
        "elapsed_time":    result["elapsed_time"],
    }



def print_comparison(state_name, depth, mm_result, ab_result):
    print(f"\n{'=' * 55}")
    print(f"  STATE: {state_name}")
    print(f"  DEPTH: {depth}")
    print(f"{'=' * 55}")

    # Minimax
    print(f"\n  MINIMAX")
    print(f"    Move   : {mm_result['move']}")
    print(f"    Score  : {mm_result['score']}")
    print(f"    States : {mm_result['states_explored']:,}")
    print(f"    Time   : {mm_result['elapsed_time']:.4f}s")

    # Alpha-Beta
    print(f"\n  ALPHABETA")
    print(f"    Move   : {ab_result['move']}")
    print(f"    Score  : {ab_result['score']}")
    print(f"    States : {ab_result['states_explored']:,}")
    print(f"    Time   : {ab_result['elapsed_time']:.4f}s")

    # So sánh
    if mm_result['states_explored'] > 0:
        state_reduction = (1 - ab_result['states_explored'] / mm_result['states_explored']) * 100
    else:
        state_reduction = 0

    if mm_result['elapsed_time'] > 0:
        time_reduction = (1 - ab_result['elapsed_time'] / mm_result['elapsed_time']) * 100
    else:
        time_reduction = 0

    same_move = "YES" if mm_result['move'] == ab_result['move'] else "NO"

    print(f"\n  --- SO SANH ---")
    print(f"    Same move?       : {same_move}")
    print(f"    States giam      : {state_reduction:.1f}%")
    print(f"    Time giam        : {time_reduction:.1f}%")



def run_benchmark():
    print()
    print("=" * 55)
    print("       CARO AI — BENCHMARK")
    print("       Minimax vs Alpha-Beta Pruning")
    print("=" * 55)

    all_results = []

    for state_name, state_fn in TEST_STATES:
        for depth in DEPTHS:
            # Tạo board mới cho mỗi lần chạy
            board = state_fn()

            # Minimax
            mm = run_single("minimax", minimax_get_best_move, board, depth)
            mm["state"] = state_name

            # Alpha-Beta
            ab = run_single("alphabeta", alphabeta_get_best_move, board, depth)
            ab["state"] = state_name

            all_results.append(mm)
            all_results.append(ab)

            print_comparison(state_name, depth, mm, ab)

    # In bảng tổng hợp
    print_summary_table(all_results)

    # Xuất CSV
    export_csv(all_results)

    print(f"\n{'=' * 55}")
    print("  BENCHMARK HOAN TAT!")
    print(f"{'=' * 55}\n")




def print_summary_table(results):
    print(f"\n\n{'=' * 90}")
    print("  BANG TONG HOP")
    print(f"{'=' * 90}")

    header = f"{'State':<15} {'Algorithm':<12} {'Depth':<6} {'Move':<10} {'Score':<12} {'States':<12} {'Time':<10}"
    print(f"  {header}")
    print(f"  {'-' * 85}")

    for r in results:
        move_str = f"({r['move'][0]},{r['move'][1]})"
        line = (
            f"  {r['state']:<15} "
            f"{r['algorithm']:<12} "
            f"{r['depth']:<6} "
            f"{move_str:<10} "
            f"{r['score']:<12} "
            f"{r['states_explored']:<12,} "
            f"{r['elapsed_time']:<10.4f}"
        )
        print(line)



def export_csv(results):
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["State", "Algorithm", "Depth", "Move", "Score", "States_Explored", "Time_s"])

        for r in results:
            move_str = f"({r['move'][0]},{r['move'][1]})"
            writer.writerow([
                r["state"],
                r["algorithm"],
                r["depth"],
                move_str,
                r["score"],
                r["states_explored"],
                f"{r['elapsed_time']:.4f}",
            ])

    print(f"\n  CSV saved: {os.path.abspath(CSV_FILE)}")



if __name__ == "__main__":
    run_benchmark()
