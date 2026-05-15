import sys

from source_code.game.game_manager import GameManager
from source_code.ai.ai_player import AIPlayer
from source_code.game.board import PLAYER_X, PLAYER_O


def choose_algorithm():
    while True:
        print("Chọn thuật toán AI:")
        print("  1. Minimax")
        print("  2. Alpha-Beta")
        choice = input("Nhập lựa chọn (1/2): ").strip()

        if choice == "1":
            return "minimax"
        if choice == "2":
            return "alphabeta"

        print("Lựa chọn không hợp lệ, vui lòng nhập lại.\n")


def choose_depth():
    while True:
        raw = input("Nhập độ sâu tìm kiếm (1-4, mặc định 3): ").strip()
        if raw == "":
            return 3
        if raw.isdigit():
            depth = int(raw)
            if 1 <= depth <= 4:
                return depth
        print("Độ sâu không hợp lệ, vui lòng nhập lại.\n")


def main():
    print()
    print("╔══════════════════════════════════════════╗")
    print("║          Welcome to Caro AI              ║")
    print("╚══════════════════════════════════════════╝")
    print()

    algorithm = choose_algorithm()
    print()
    depth = choose_depth()
    print()

    print(f"  Chế độ    : Người (X) vs Máy (O)")
    print(f"  Thuật toán: {algorithm}")
    print(f"  Độ sâu    : {depth}")
    print()

    ai = AIPlayer(
        algorithm=algorithm,
        depth=depth,
        ai_player=PLAYER_O,
        human_player=PLAYER_X,
    )

    game = GameManager(
        board_size=15,
        human_player=PLAYER_X,
        ai_player=PLAYER_O,
        algorithm=algorithm,
        depth=depth,
        ai_module=ai,
    )

    game.start_game()


if __name__ == "__main__":
    main()
