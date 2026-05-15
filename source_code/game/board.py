

# -------------------- Khối 1: Hằng số --------------------
EMPTY    = '.'
PLAYER_X = 'X'   
PLAYER_O = 'O'   


class Board:


    # -------------------- Khối 2: Khởi tạo --------------------
    def __init__(self, size=15):

        self.size = size
        self.grid = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.move_history = []

    # -------------------- Khối 3: Kiểm tra --------------------
    def is_in_bounds(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def is_empty(self, row, col):
        if not self.is_in_bounds(row, col):
            return False
        return self.grid[row][col] == EMPTY

    def is_valid_move(self, row, col):
        return self.is_in_bounds(row, col) and self.is_empty(row, col)

    # -------------------- Khối 4: Thao tác --------------------
    def make_move(self, row, col, player):
        if player not in (PLAYER_X, PLAYER_O):
            raise ValueError(f"Quân cờ không hợp lệ: '{player}'. Chỉ chấp nhận '{PLAYER_X}' hoặc '{PLAYER_O}'.")

        if not self.is_valid_move(row, col):
            return False

        self.grid[row][col] = player
        self.move_history.append((row, col, player))
        return True

    def undo_move(self):
        if not self.move_history:
            return None

        row, col, player = self.move_history.pop()
        self.grid[row][col] = EMPTY
        return (row, col, player)

    # -------------------- Khối 5: Trạng thái --------------------
    def is_full(self):
        """Kiểm tra bàn cờ đã đầy chưa (dùng để xác định hòa)."""
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == EMPTY:
                    return False
        return True

    def get_cell(self, row, col):
        if not self.is_in_bounds(row, col):
            return None
        return self.grid[row][col]

    def get_valid_moves(self):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == EMPTY:
                    moves.append((r, c))
        return moves

    # -------------------- Khối 6: Hiển thị --------------------
    def display(self):
        # In header cột
        header = "     " + "  ".join(f"{c:>2}" for c in range(self.size))
        print(header)

        # In từng hàng
        for r in range(self.size):
            row_str = f"{r:>3}   " + "  ".join(f"{self.grid[r][c]:>2}" for c in range(self.size))
            print(row_str)

        print()  # Dòng trống cho dễ nhìn
