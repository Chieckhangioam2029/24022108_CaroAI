import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from source_code.game.board import Board, PLAYER_X, PLAYER_O


#  State 1: Opening — Ít quân, giai đoạn mở đầu

def state_opening():
    board = Board(size=15)

    board.make_move(7, 7, PLAYER_X)
    board.make_move(7, 8, PLAYER_O)

    return board


#  State 2: Midgame — Nhiều quân, trung cuộc phức tạp

def state_midgame():
    board = Board(size=15)

    # X đánh
    board.make_move(7, 7, PLAYER_X)
    board.make_move(6, 6, PLAYER_O)

    board.make_move(8, 8, PLAYER_X)
    board.make_move(6, 8, PLAYER_O)

    board.make_move(6, 7, PLAYER_X)
    board.make_move(8, 6, PLAYER_O)

    board.make_move(9, 5, PLAYER_X)
    board.make_move(5, 9, PLAYER_O)

    board.make_move(8, 7, PLAYER_X)
    board.make_move(9, 7, PLAYER_O)

    board.make_move(5, 5, PLAYER_X)
    board.make_move(10, 6, PLAYER_O)

    return board


#  State 3: AI có thể thắng ngay (O O O .)

def state_ai_can_win():
    board = Board(size=15)

    # O có 3 quân liên tiếp ngang, 1 ô trống bên phải → thắng nếu đánh (7,10)
    board.make_move(7, 7, PLAYER_O)
    board.make_move(6, 6, PLAYER_X)

    board.make_move(7, 8, PLAYER_O)
    board.make_move(6, 7, PLAYER_X)

    board.make_move(7, 9, PLAYER_O)
    board.make_move(5, 5, PLAYER_X)

    return board


#  State 4: AI phải chặn (X X X .)

def state_need_block():
    board = Board(size=15)

    # X có 3 quân ngang → AI phải chặn tại (7,10) hoặc (7,6)
    board.make_move(7, 7, PLAYER_X)
    board.make_move(6, 6, PLAYER_O)

    board.make_move(7, 8, PLAYER_X)
    board.make_move(5, 5, PLAYER_O)

    board.make_move(7, 9, PLAYER_X)
    board.make_move(5, 6, PLAYER_O)

    return board


#  State 5: Complex — Nhiều hướng tấn công

def state_complex():
    board = Board(size=15)

    # X tạo double threat: ngang + chéo
    board.make_move(7, 7, PLAYER_X)
    board.make_move(6, 5, PLAYER_O)

    board.make_move(7, 8, PLAYER_X)
    board.make_move(6, 9, PLAYER_O)

    board.make_move(8, 8, PLAYER_X)
    board.make_move(5, 5, PLAYER_O)

    board.make_move(9, 9, PLAYER_X)
    board.make_move(10, 10, PLAYER_O)

    board.make_move(6, 7, PLAYER_X)
    board.make_move(5, 8, PLAYER_O)

    board.make_move(8, 6, PLAYER_X)
    board.make_move(9, 5, PLAYER_O)

    return board


# Registry — Danh sách tất cả states

TEST_STATES = [
    ("OPENING",       state_opening),
    ("MIDGAME",       state_midgame),
    ("AI_CAN_WIN",    state_ai_can_win),
    ("NEED_BLOCK",    state_need_block),
    ("COMPLEX",       state_complex),
]
