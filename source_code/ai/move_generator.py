
from source_code.game.board import Board, EMPTY, PLAYER_X, PLAYER_O
from source_code.game.rules import check_winner


DIRECTIONS_8 = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

DIRECTIONS_4 = [
    (0, 1),
    (1, 0),
    (1, 1),
    (1, -1),
]

# Issue #9: increased from 15 to 25
MAX_CANDIDATES = 25

WIN_LENGTH = 4

# Forced move score threshold
FORCED_THRESHOLD = 900_000


def is_board_empty(board: Board) -> bool:
    return len(board.move_history) == 0


def _count_in_direction(board, row, col, dr, dc, player):
    count = 0
    r, c = row + dr, col + dc
    while 0 <= r < board.size and 0 <= c < board.size and board.grid[r][c] == player:
        count += 1
        r += dr
        c += dc
    return count


def _line_info(board, row, col, dr, dc, player):
    count_fwd = _count_in_direction(board, row, col, dr, dc, player)
    count_bwd = _count_in_direction(board, row, col, -dr, -dc, player)
    total = count_fwd + count_bwd

    fr, fc = row + dr * (count_fwd + 1), col + dc * (count_fwd + 1)
    open_fwd = (0 <= fr < board.size and 0 <= fc < board.size and board.grid[fr][fc] == EMPTY)

    br, bc = row - dr * (count_bwd + 1), col - dc * (count_bwd + 1)
    open_bwd = (0 <= br < board.size and 0 <= bc < board.size and board.grid[br][bc] == EMPTY)

    open_ends = int(open_fwd) + int(open_bwd)
    return total, open_ends


# -------------------- Issue #5: Forced move detection --------------------

def _get_neighbor_cells(board: Board, radius: int = 1) -> set[tuple[int, int]]:
    """Get all empty cells within radius of existing pieces."""
    candidate_set = set()
    size = board.size
    grid = board.grid
    for row, col, _ in board.move_history:
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == EMPTY:
                    candidate_set.add((nr, nc))
    return candidate_set


def find_winning_moves(board: Board, player) -> list[tuple[int, int]]:
    """Find all moves that immediately win for player."""
    winning = []
    candidates = _get_neighbor_cells(board)
    for row, col in candidates:
        board.make_move(row, col, player)
        if check_winner(board) == player:
            winning.append((row, col))
        board.undo_move()
    return winning


# -------------------- Issue #6: Immediate block detection --------------------

def find_blocking_moves(board: Board, player, opponent) -> list[tuple[int, int]]:
    """Find all moves that block opponent's immediate win."""
    blocking = []
    candidates = _get_neighbor_cells(board)
    for row, col in candidates:
        board.make_move(row, col, opponent)
        if check_winner(board) == opponent:
            blocking.append((row, col))
        board.undo_move()
    return blocking


# -------------------- Issue #7 & #8: Redesigned quick_move_score --------------------

def quick_move_score(board: Board, row: int, col: int,
                     current_player, opponent) -> int:
    """
    Score a candidate move for move ordering.
    Higher score = more promising move.

    Issue #8: current_player and opponent are passed explicitly.
    Issue #7: redesigned priority tiers.
    """
    score = 0
    size = board.size
    grid = board.grid

    if not board.move_history:
        center = size // 2
        return -(abs(row - center) + abs(col - center))

    # --- Offensive tactical value ---
    board.grid[row][col] = current_player

    for dr, dc in DIRECTIONS_4:
        total, open_ends = _line_info(board, row, col, dr, dc, current_player)
        if total >= WIN_LENGTH - 1:
            board.grid[row][col] = EMPTY
            return 1_000_000           # WIN_NOW
        if total == WIN_LENGTH - 2 and open_ends == 2:
            score += 100_000           # OPEN_THREE
        elif total == WIN_LENGTH - 2 and open_ends == 1:
            score += 10_000            # CLOSED_THREE
        elif total == 1 and open_ends == 2:
            score += 5_000             # OPEN_TWO
        elif total == 1 and open_ends == 1:
            score += 500               # CLOSED_TWO

    board.grid[row][col] = EMPTY

    # --- Defensive blocking value ---
    board.grid[row][col] = opponent

    for dr, dc in DIRECTIONS_4:
        total, open_ends = _line_info(board, row, col, dr, dc, opponent)
        if total >= WIN_LENGTH - 1:
            board.grid[row][col] = EMPTY
            return 900_000             # BLOCK_WIN
        if total == WIN_LENGTH - 2 and open_ends == 2:
            score += 80_000            # BLOCK_OPEN_THREE
        elif total == WIN_LENGTH - 2 and open_ends == 1:
            score += 8_000             # BLOCK_CLOSED_THREE
        elif total == 1 and open_ends == 2:
            score += 4_000             # BLOCK_OPEN_TWO

    board.grid[row][col] = EMPTY

    # Neighbor density bonus
    neighbor_count = 0
    for dr, dc in DIRECTIONS_8:
        nr, nc = row + dr, col + dc
        if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] != EMPTY:
            neighbor_count += 1
    score += neighbor_count * 10

    # Center proximity bonus
    center = size // 2
    score -= abs(row - center) + abs(col - center)

    return score


# -------------------- Issue #8 & #9: Candidate generation --------------------

def get_candidate_moves(board: Board, current_player=None, opponent=None,
                        radius: int = 1) -> list[tuple[int, int]]:
    """
    Generate and sort candidate moves by tactical priority.

    Issue #8: accepts current_player/opponent explicitly.
    Issue #9: MAX_CANDIDATES=25, forced moves never pruned.
    """
    if is_board_empty(board):
        center = board.size // 2
        return [(center, center)]

    # Infer players if not provided (backward compatibility)
    if current_player is None or opponent is None:
        if board.move_history:
            last_player = board.move_history[-1][2]
            current_player = PLAYER_O if last_player == PLAYER_X else PLAYER_X
            opponent = last_player
        else:
            current_player = PLAYER_X
            opponent = PLAYER_O

    candidate_set = _get_neighbor_cells(board, radius)

    # Score all candidates
    scored = [
        (pos, quick_move_score(board, pos[0], pos[1], current_player, opponent))
        for pos in candidate_set
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    if len(scored) <= MAX_CANDIDATES:
        return [pos for pos, _ in scored]

    # Keep top MAX_CANDIDATES + any forced moves beyond the limit
    result = []
    for i, (pos, s) in enumerate(scored):
        if i < MAX_CANDIDATES or s >= FORCED_THRESHOLD:
            result.append(pos)

    return result
