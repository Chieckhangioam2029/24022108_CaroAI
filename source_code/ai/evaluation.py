from source_code.game.board import EMPTY, PLAYER_X, PLAYER_O
from source_code.game.rules import check_winner


WIN_LENGTH = 4

# -------------------- Score Constants (Issue #4) --------------------
SCORE_WIN          = 1_000_000

SCORE_OPEN_THREE   = 20_000
SCORE_CLOSED_THREE = 5_000
SCORE_BROKEN_THREE = 3_000

SCORE_OPEN_TWO     = 500
SCORE_CLOSED_TWO   = 100

SCORE_ONE          = 10

# -------------------- Defense Multiplier (Issue #3) --------------------
DEFENSE_MULTIPLIER = 2.0

DIRECTIONS = [
    (0, 1),
    (1, 0),
    (1, 1),
    (1, -1),
]


# -------------------- Pattern-based window evaluation (Issues #1, #2) --------------------

def _to_pattern(window, player):
    """Convert window cells to pattern string relative to player."""
    chars = []
    for cell in window:
        if cell == player:
            chars.append('P')
        elif cell == EMPTY:
            chars.append('.')
        else:
            chars.append('O')
    return ''.join(chars)


def evaluate_window_pattern(window, left_open, right_open, player):
    """
    Score a single window of WIN_LENGTH cells using pattern matching.

    Distinguishes connected vs broken patterns and open vs closed ends.
    Returns a non-negative score (caller applies sign and defense multiplier).
    """
    pattern = _to_pattern(window, player)

    p_count = pattern.count('P')
    o_count = pattern.count('O')

    # Mixed window — no value for either side
    if p_count > 0 and o_count > 0:
        return 0

    if p_count == 0:
        return 0

    open_ends = int(left_open) + int(right_open)

    # --- WIN (all cells filled) ---
    if p_count == WIN_LENGTH:
        return SCORE_WIN

    # --- THREE patterns (3 pieces, 1 empty in window) ---
    if p_count == 3:
        # Connected three: PPP. or .PPP
        if pattern in ('PPP.', '.PPP'):
            if open_ends == 2:
                return SCORE_OPEN_THREE
            elif open_ends >= 1:
                return SCORE_CLOSED_THREE
            else:
                return SCORE_CLOSED_THREE // 2
        # Broken three: PP.P or P.PP
        if pattern in ('PP.P', 'P.PP'):
            if open_ends >= 1:
                return SCORE_BROKEN_THREE
            else:
                return SCORE_BROKEN_THREE // 2

    # --- TWO patterns (2 pieces, 2 empty in window) ---
    if p_count == 2:
        if pattern in ('.PP.', 'PP..', '..PP'):
            if open_ends == 2:
                return SCORE_OPEN_TWO
            elif open_ends >= 1:
                return SCORE_CLOSED_TWO
            else:
                return SCORE_CLOSED_TWO // 2
        # Other spread patterns (P..P, P.P., .P.P)
        return SCORE_CLOSED_TWO // 2

    # --- ONE (1 piece, 3 empty) ---
    if p_count == 1:
        return SCORE_ONE

    return 0


# -------------------- Relevant cells collector --------------------

def _collect_relevant_cells(board):
    relevant = set()
    size = board.size
    for row, col, _ in board.move_history:
        for dr, dc in DIRECTIONS:
            for start_offset in range(-(WIN_LENGTH - 1), 1):
                sr = row + dr * start_offset
                sc = col + dc * start_offset
                er = sr + dr * (WIN_LENGTH - 1)
                ec = sc + dc * (WIN_LENGTH - 1)
                if 0 <= sr < size and 0 <= sc < size and 0 <= er < size and 0 <= ec < size:
                    relevant.add((sr, sc, dr, dc))
    return relevant


# -------------------- Board evaluation --------------------

def evaluate_board(board, ai_player, human_player):
    """
    Evaluate the board from ai_player's perspective.
    Uses pattern-based window evaluation with open-end detection.
    """
    winner = check_winner(board)
    if winner == ai_player:
        return SCORE_WIN
    if winner == human_player:
        return -int(SCORE_WIN * DEFENSE_MULTIPLIER)

    total_score = 0
    size = board.size
    grid = board.grid
    seen = _collect_relevant_cells(board)

    for sr, sc, dr, dc in seen:
        # Build the window
        window = []
        for i in range(WIN_LENGTH):
            window.append(grid[sr + dr * i][sc + dc * i])

        # Check open ends (Issue #2)
        lr, lc = sr - dr, sc - dc
        left_open = (0 <= lr < size and 0 <= lc < size and grid[lr][lc] == EMPTY)

        rr, rc = sr + dr * WIN_LENGTH, sc + dc * WIN_LENGTH
        right_open = (0 <= rr < size and 0 <= rc < size and grid[rr][rc] == EMPTY)

        # Score for AI (positive)
        ai_score = evaluate_window_pattern(window, left_open, right_open, ai_player)
        # Score for human threats (negative with defense multiplier)
        human_score = evaluate_window_pattern(window, left_open, right_open, human_player)

        total_score += ai_score
        total_score -= int(human_score * DEFENSE_MULTIPLIER)

    return total_score
