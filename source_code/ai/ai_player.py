from source_code.ai.minimax import get_best_move as minimax_best_move
from source_code.ai.alphabeta import get_best_move as alphabeta_best_move
from source_code.game.board import PLAYER_X, PLAYER_O


class AIPlayer:

    def __init__(self, algorithm="alphabeta", depth=3, ai_player=PLAYER_O, human_player=PLAYER_X):
        self.algorithm = algorithm
        self.depth = depth
        self.ai_player = ai_player
        self.human_player = human_player

    def get_move(self, board):
        if self.algorithm == "minimax":
            return minimax_best_move(board, self.depth, self.ai_player, self.human_player)

        if self.algorithm == "alphabeta":
            return alphabeta_best_move(board, self.depth, self.ai_player, self.human_player)

        raise ValueError(f"Unknown algorithm: '{self.algorithm}'")
