import time
import random

from source_code.game.board import Board, PLAYER_X, PLAYER_O, EMPTY
from source_code.game.rules import check_winner, check_draw, is_terminal


class GameManager:

    #  Khối 1: Khởi tạo
    def __init__(self, board_size=15, human_player=PLAYER_X, ai_player=PLAYER_O,
                 algorithm="minimax", depth=3, ai_module=None):
        # --- Bàn cờ ---
        self.board = Board(size=board_size)

        # --- Người chơi ---
        self.human_player = human_player
        self.ai_player    = ai_player
        self.current_player = PLAYER_X          # X luôn đi trước

        # --- Cấu hình AI ---
        self.algorithm  = algorithm
        self.depth      = depth
        self.ai_module  = ai_module             # ai_player.AIPlayer instance

        # --- Trạng thái trận đấu ---
        self.game_over  = False
        self.winner     = None                  # PLAYER_X / PLAYER_O / None (hòa)

        # --- Thống kê AI ---
        self.ai_stats = {
            "last_move":        None,
            "last_score":       None,
            "states_explored":  0,
            "elapsed_time":     0.0,
        }

    #  Khối 2: Vòng lặp chính
    def start_game(self):

        print("=" * 50)
        print("         CARO AI — BẮT ĐẦU TRẬN ĐẤU  ")
        print("=" * 50)
        print(f"  Người chơi : {self.human_player}")
        print(f"  Máy        : {self.ai_player}")
        print(f"  Thuật toán : {self.algorithm}")
        print(f"  Độ sâu     : {self.depth}")
        print(f"  Bàn cờ     : {self.board.size}×{self.board.size}")
        print("=" * 50)
        print()

        while not self.game_over:
            # --- Bước 1: in bàn cờ ---
            self.board.display()

            # --- Bước 2–3: xử lý lượt ---
            if self.current_player == self.human_player:
                self.handle_human_turn()
            else:
                self.handle_ai_turn()

            # --- Bước 4: kiểm tra kết thúc ---
            if self.check_game_over():
                break

            # --- Bước 5: đổi lượt ---
            self.switch_player()

        self.board.display()
        self.print_result()

    # Khối 3: Xử lý lượt người chơi
    def handle_human_turn(self):

        while True:
            try:
                raw = input(f"[{self.human_player}] Nhập nước đi (hàng cột, ví dụ: 7 7): ")
                parts = raw.strip().split()

                if len(parts) != 2:
                    print("    Vui lòng nhập đúng 2 số: hàng và cột (cách nhau bằng dấu cách).")
                    continue

                row, col = int(parts[0]), int(parts[1])

                # Kiểm tra biên
                if not self.board.is_in_bounds(row, col):
                    print(f"    Tọa độ ({row}, {col}) nằm ngoài bàn cờ "
                          f"(0–{self.board.size - 1}).")
                    continue

                # Kiểm tra ô trống
                if not self.board.is_empty(row, col):
                    print(f"    Ô ({row}, {col}) đã có quân '{self.board.get_cell(row, col)}'.")
                    continue

                # Đặt quân
                success = self.board.make_move(row, col, self.human_player)
                if success:
                    print(f"    Bạn đã đánh [{self.human_player}] tại ({row}, {col}).")
                    return
                else:
                    print("    Không thể đặt quân. Thử lại.")

            except ValueError:
                print("    Vui lòng nhập số nguyên hợp lệ.")
            except KeyboardInterrupt:
                print("\n\n    Trận đấu đã bị hủy bởi người chơi.")
                self.game_over = True
                return

    #  Khối 4: Xử lý lượt máy
    def handle_ai_turn(self):

        print(f"\n    Máy [{self.ai_player}] đang suy nghĩ...")

        start_time = time.time()

        if self.ai_module is not None:
            result = self.ai_module.get_move(self.board)

            if isinstance(result, tuple) and len(result) == 2:
                row, col = result
                score = None
                states = 0
            elif isinstance(result, dict):
                row   = result.get("row")
                col   = result.get("col")
                score = result.get("score")
                states = result.get("states_explored", 0)
            else:
                row, col = result[0], result[1]
                score = None
                states = 0
        else:
            # ---- AI tạm thời: đánh random ----
            move = self._random_move()
            if move is None:
                print("    Không còn ô trống để đánh!")
                return
            row, col = move
            score  = None
            states = 0

        elapsed = time.time() - start_time

        # Đặt quân
        success = self.board.make_move(row, col, self.ai_player)
        if not success:
            print(f"    AI trả về nước đi không hợp lệ ({row}, {col})!")
            # Fallback: đánh random
            move = self._random_move()
            if move is None:
                print("    Không còn ô trống để đánh!")
                return
            row, col = move
            self.board.make_move(row, col, self.ai_player)
            elapsed = time.time() - start_time

        # Cập nhật thống kê
        self.ai_stats["last_move"]       = (row, col)
        self.ai_stats["last_score"]      = score
        self.ai_stats["states_explored"] = states
        self.ai_stats["elapsed_time"]    = elapsed

        # In thông tin
        print(f"  ✔  Máy đã đánh [{self.ai_player}] tại ({row}, {col})")
        print(f"        Thời gian : {elapsed:.3f}s")
        if score is not None:
            print(f"       Score     : {score}")
        if states > 0:
            print(f"       States    : {states:,}")
        print()

    #  Khối 5: Đổi lượt
    def switch_player(self):
        """
        Đổi lượt chơi: X → O, O → X.
        Tách riêng để vòng lặp chính không bị rối.
        """
        if self.current_player == PLAYER_X:
            self.current_player = PLAYER_O
        else:
            self.current_player = PLAYER_X

    #  Khối 6: Kiểm tra kết thúc
    def check_game_over(self):

        is_over, winner = is_terminal(self.board)

        if is_over:
            self.game_over = True
            self.winner = winner        # player hoặc None (hòa)
            return True

        return False

    #  Khối 7: In kết quả
    
    def print_result(self):

        print()
        print("=" * 50)

        if self.winner is None:
            print("         KẾT QUẢ: HÒA!")
        elif self.winner == self.human_player:
            print(f"         KẾT QUẢ: NGƯỜI CHƠI [{self.human_player}] THẮNG!")
        else:
            print(f"         KẾT QUẢ: MÁY [{self.ai_player}] THẮNG!")

        print("=" * 50)

        # In thống kê AI nước cuối
        if self.ai_stats["last_move"] is not None:
            print()
            print("    Thống kê AI (nước cuối):")
            print(f"      Nước đi     : {self.ai_stats['last_move']}")
            if self.ai_stats["last_score"] is not None:
                print(f"      Score       : {self.ai_stats['last_score']}")
            if self.ai_stats["states_explored"] > 0:
                print(f"      States      : {self.ai_stats['states_explored']:,}")
            print(f"      Thời gian   : {self.ai_stats['elapsed_time']:.3f}s")

        total_moves = len(self.board.move_history)
        print(f"\n   Tổng số nước đi: {total_moves}")
        print()

    # ================================================================
    #  Khối 8: Hàm helper
    # ================================================================
    def _random_move(self):
        """
        AI tạm thời: chọn ngẫu nhiên ô trống.
        Dùng khi chưa nối Minimax / Alpha-Beta.
        """
        empty_cells = []
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.is_empty(r, c):
                    empty_cells.append((r, c))

        if not empty_cells:
            return None

        return random.choice(empty_cells)
