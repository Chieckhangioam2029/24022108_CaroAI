

# -------------------- Khối 1: Hằng số --------------------
EMPTY    = '.'
PLAYER_X = 'X'   
PLAYER_O = 'O'  

WIN_LENGTH = 4

# 4 hướng kiểm tra: ngang, dọc, chéo chính, chéo phụ
DIRECTIONS = [
    (0, 1),   
    (1, 0),   
    (1, 1),   
    (1, -1),  
]


# -------------------- Khối 2: Kiểm tra thắng --------------------
def _count_consecutive(board, row, col, dr, dc, player):

    count = 0
    r, c = row + dr, col + dc
    while board.is_in_bounds(r, c) and board.get_cell(r, c) == player:
        count += 1
        r += dr
        c += dc
    return count


def check_winner_at(board, row, col):

    player = board.get_cell(row, col)
    if player == EMPTY or player is None:
        return None

    for dr, dc in DIRECTIONS:
        # Đếm cả 2 chiều + bản thân ô hiện tại
        total = 1
        total += _count_consecutive(board, row, col, dr, dc, player)
        total += _count_consecutive(board, row, col, -dr, -dc, player)

        if total >= WIN_LENGTH:
            return player

    return None


def check_winner(board):

    if board.move_history:
        last_row, last_col, last_player = board.move_history[-1]
        result = check_winner_at(board, last_row, last_col)
        if result:
            return result

    return None


def check_winner_full_scan(board):
    for r in range(board.size):
        for c in range(board.size):
            result = check_winner_at(board, r, c)
            if result:
                return result
    return None


# -------------------- Khối 3: Kiểm tra hòa --------------------
def check_draw(board):

    return board.is_full() and check_winner(board) is None


# -------------------- Khối 4: Kiểm tra terminal --------------------
def is_terminal(board):
    winner = check_winner(board)
    if winner:
        return True, winner

    if board.is_full():
        return True, None   # hòa

    return False, None      # chưa kết thúc