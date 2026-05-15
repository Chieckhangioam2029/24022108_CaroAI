import pygame
import sys
import time
import threading

from source_code.game.game_manager import GameManager
from source_code.ai.ai_player import AIPlayer
from source_code.game.board import Board, PLAYER_X, PLAYER_O, EMPTY
from source_code.game.rules import check_winner_at, is_terminal

BOARD_SIZE = 15
CELL_SIZE = 50
MARGIN = 50
PANEL_HEIGHT = 140
BOARD_PIXEL = BOARD_SIZE * CELL_SIZE
WIDTH = BOARD_PIXEL + MARGIN * 2
HEIGHT = BOARD_PIXEL + MARGIN * 2 + PANEL_HEIGHT

BG_COLOR = (222, 184, 135)
LINE_COLOR = (60, 40, 20)
GRID_DOT_COLOR = (60, 40, 20)
X_COLOR = (20, 20, 20)
O_COLOR = (200, 35, 35)
HIGHLIGHT_COLOR = (255, 215, 0)
PANEL_BG = (40, 40, 40)
PANEL_TEXT = (220, 220, 220)
PANEL_ACCENT = (100, 200, 120)
WIN_LINE_COLOR = (50, 205, 50)
BUTTON_COLOR = (80, 160, 80)
BUTTON_HOVER = (100, 200, 100)
BUTTON_TEXT = (255, 255, 255)
MENU_BG = (30, 30, 45)
MENU_TITLE_COLOR = (100, 220, 140)
MENU_BTN = (55, 65, 90)
MENU_BTN_HOVER = (75, 90, 130)
MENU_BTN_ACTIVE = (80, 160, 80)
MENU_LABEL = (180, 180, 200)

STAR_POINTS = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]


class CaroGame:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Caro AI")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_stat = pygame.font.SysFont("Segoe UI", 18)
        self.font_big = pygame.font.SysFont("Segoe UI", 52, bold=True)
        self.font_btn = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 16)
        self.font_coord = pygame.font.SysFont("Consolas", 12)
        self.font_menu_title = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.font_menu_btn = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_menu_label = pygame.font.SysFont("Segoe UI", 20)

        self.state = "menu"
        self.game_mode = "hva"
        self.algorithm = "alphabeta"
        self.depth = 3
        self.ai_x_algo = "alphabeta"
        self.ai_x_depth = 3
        self.ai_o_algo = "alphabeta"
        self.ai_o_depth = 3
        self.first_player = PLAYER_X
        self.ai_config_label = ""
        self.ai_thinking = False
        self.ai_thread = None

        self.menu_buttons = {}
        self.init_game_state()

    def init_game_state(self):
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.win_cells = []
        self.hover_pos = None
        self.ai_thinking = False
        self.stats = {"algorithm": self.algorithm, "depth": self.depth, "states": 0, "time": 0.0, "score": None}

    def start_game_with_config(self):
        self.init_game_state()
        if self.game_mode == "hvh":
            self.manager = GameManager(board_size=BOARD_SIZE, human_player=PLAYER_X, ai_player=PLAYER_O,
                                       algorithm="alphabeta", depth=3, ai_module=None)
            self.ai_config_label = ""
            print("[CONFIG] Mode: Human vs Human")
        elif self.game_mode == "hva":
            ai = AIPlayer(algorithm=self.algorithm, depth=self.depth, ai_player=PLAYER_O, human_player=PLAYER_X)
            self.manager = GameManager(board_size=BOARD_SIZE, human_player=PLAYER_X, ai_player=PLAYER_O,
                                       algorithm=self.algorithm, depth=self.depth, ai_module=ai)
            self.ai_o = ai
            self.ai_config_label = f"O: {self.algorithm.upper()}-{self.depth}"
            print(f"[CONFIG] Mode: Human vs AI | O: {self.algorithm} depth={self.depth}")
        else:
            self.ai_x = AIPlayer(algorithm=self.ai_x_algo, depth=self.ai_x_depth, ai_player=PLAYER_X, human_player=PLAYER_O)
            self.ai_o = AIPlayer(algorithm=self.ai_o_algo, depth=self.ai_o_depth, ai_player=PLAYER_O, human_player=PLAYER_X)
            self.manager = GameManager(board_size=BOARD_SIZE, human_player=PLAYER_X, ai_player=PLAYER_O,
                                       algorithm=self.ai_o_algo, depth=self.ai_o_depth, ai_module=self.ai_o)
            self.ai_config_label = f"X: {self.ai_x_algo.upper()}-{self.ai_x_depth}  O: {self.ai_o_algo.upper()}-{self.ai_o_depth}"
            print(f"[CONFIG] Mode: AI vs AI | X: {self.ai_x_algo} depth={self.ai_x_depth} | O: {self.ai_o_algo} depth={self.ai_o_depth}")
        self.manager.current_player = self.first_player
        self.state = "playing"
        if self.game_mode == "ava":
            self.start_ai_turn()
        elif self.game_mode == "hva" and self.first_player == PLAYER_O:
            self.start_ai_turn()

    def board_to_pixel(self, row, col):
        x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
        y = MARGIN + row * CELL_SIZE + CELL_SIZE // 2
        return x, y

    def pixel_to_board(self, mx, my):
        if mx < MARGIN or my < MARGIN:
            return None, None
        if mx >= MARGIN + BOARD_PIXEL or my >= MARGIN + BOARD_PIXEL:
            return None, None
        col = (mx - MARGIN) // CELL_SIZE
        row = (my - MARGIN) // CELL_SIZE
        return row, col

    def get_win_cells(self, board, row, col):
        player = board.get_cell(row, col)
        if player == EMPTY or player is None:
            return []
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            cells = [(row, col)]
            r, c = row + dr, col + dc
            while board.is_in_bounds(r, c) and board.get_cell(r, c) == player:
                cells.append((r, c))
                r += dr
                c += dc
            r, c = row - dr, col - dc
            while board.is_in_bounds(r, c) and board.get_cell(r, c) == player:
                cells.append((r, c))
                r -= dr
                c -= dc
            if len(cells) >= 4:
                return cells
        return []

    # ==================== MENU ====================

    def draw_menu(self):
        self.menu_buttons = {}
        self.screen.fill(MENU_BG)
        title = self.font_menu_title.render("CARO AI", True, MENU_TITLE_COLOR)
        self.screen.blit(title, ((WIDTH - title.get_width()) // 2, 40))

        subtitle = self.font_small.render("Minimax & Alpha-Beta Pruning", True, (120, 120, 150))
        self.screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, 95))

        cy = 150
        self.screen.blit(self.font_menu_label.render("Game Mode", True, MENU_LABEL), (WIDTH // 2 - 150, cy))
        cy += 35
        modes = [("hvh", "Human vs Human"), ("hva", "Human vs AI"), ("ava", "AI vs AI")]
        self.menu_buttons["modes"] = []
        bx = WIDTH // 2 - 230
        for key, label in modes:
            r = pygame.Rect(bx, cy, 150, 40)
            self.menu_buttons["modes"].append((r, key))
            active = self.game_mode == key
            mx, my = pygame.mouse.get_pos()
            color = MENU_BTN_ACTIVE if active else (MENU_BTN_HOVER if r.collidepoint(mx, my) else MENU_BTN)
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            t = self.font_small.render(label, True, BUTTON_TEXT)
            self.screen.blit(t, (r.x + (r.w - t.get_width()) // 2, r.y + (r.h - t.get_height()) // 2))
            bx += 160

        cy += 65
        if self.game_mode == "hva":
            self._draw_algo_depth_row(cy, "AI", "algorithm", "depth")
            cy += 100
        elif self.game_mode == "ava":
            self._draw_algo_depth_row(cy, "AI (X)", "ai_x_algo", "ai_x_depth")
            cy += 100
            self._draw_algo_depth_row(cy, "AI (O)", "ai_o_algo", "ai_o_depth")
            cy += 100

        self.screen.blit(self.font_menu_label.render("First Player", True, MENU_LABEL), (WIDTH // 2 - 150, cy))
        cy += 35
        self.menu_buttons["first"] = []
        bx = WIDTH // 2 - 110
        for key, label in [(PLAYER_X, "X goes first"), (PLAYER_O, "O goes first")]:
            r = pygame.Rect(bx, cy, 150, 40)
            self.menu_buttons["first"].append((r, key))
            active = self.first_player == key
            mx, my = pygame.mouse.get_pos()
            color = MENU_BTN_ACTIVE if active else (MENU_BTN_HOVER if r.collidepoint(mx, my) else MENU_BTN)
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            t = self.font_small.render(label, True, BUTTON_TEXT)
            self.screen.blit(t, (r.x + (r.w - t.get_width()) // 2, r.y + (r.h - t.get_height()) // 2))
            bx += 170

        cy += 70
        start_r = pygame.Rect(WIDTH // 2 - 100, cy, 200, 55)
        self.menu_buttons["start"] = start_r
        mx, my = pygame.mouse.get_pos()
        sc = BUTTON_HOVER if start_r.collidepoint(mx, my) else BUTTON_COLOR
        pygame.draw.rect(self.screen, sc, start_r, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), start_r, 2, border_radius=12)
        st = self.font_menu_btn.render("START", True, BUTTON_TEXT)
        self.screen.blit(st, (start_r.x + (start_r.w - st.get_width()) // 2, start_r.y + (start_r.h - st.get_height()) // 2))

    def _draw_algo_depth_row(self, cy, label, algo_attr, depth_attr):
        self.screen.blit(self.font_menu_label.render(label, True, MENU_LABEL), (WIDTH // 2 - 150, cy))
        cy += 30
        algo_val = getattr(self, algo_attr)
        depth_val = getattr(self, depth_attr)

        btn_key = f"algo_{algo_attr}"
        self.menu_buttons[btn_key] = []
        bx = WIDTH // 2 - 150
        for key, text in [("minimax", "Minimax"), ("alphabeta", "Alpha-Beta")]:
            r = pygame.Rect(bx, cy, 140, 36)
            self.menu_buttons[btn_key].append((r, key, algo_attr))
            active = algo_val == key
            mx, my = pygame.mouse.get_pos()
            color = MENU_BTN_ACTIVE if active else (MENU_BTN_HOVER if r.collidepoint(mx, my) else MENU_BTN)
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            t = self.font_small.render(text, True, BUTTON_TEXT)
            self.screen.blit(t, (r.x + (r.w - t.get_width()) // 2, r.y + (r.h - t.get_height()) // 2))
            bx += 155

        cy += 45
        dep_key = f"depth_{depth_attr}"
        self.menu_buttons[dep_key] = []
        self.screen.blit(self.font_small.render("Depth:", True, MENU_LABEL), (WIDTH // 2 - 150, cy + 5))
        bx = WIDTH // 2 - 60
        for d in range(1, 5):
            r = pygame.Rect(bx, cy, 45, 36)
            self.menu_buttons[dep_key].append((r, d, depth_attr))
            active = depth_val == d
            mx, my = pygame.mouse.get_pos()
            color = MENU_BTN_ACTIVE if active else (MENU_BTN_HOVER if r.collidepoint(mx, my) else MENU_BTN)
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            t = self.font_small.render(str(d), True, BUTTON_TEXT)
            self.screen.blit(t, (r.x + (r.w - t.get_width()) // 2, r.y + (r.h - t.get_height()) // 2))
            bx += 55

    def handle_menu_click(self, mx, my):
        for r, key in self.menu_buttons.get("modes", []):
            if r.collidepoint(mx, my):
                self.game_mode = key
                return
        for r, key in self.menu_buttons.get("first", []):
            if r.collidepoint(mx, my):
                self.first_player = key
                return
        for bkey in self.menu_buttons:
            if bkey.startswith("algo_"):
                for r, val, attr in self.menu_buttons[bkey]:
                    if r.collidepoint(mx, my):
                        setattr(self, attr, val)
                        return
            if bkey.startswith("depth_"):
                for r, val, attr in self.menu_buttons[bkey]:
                    if r.collidepoint(mx, my):
                        setattr(self, attr, val)
                        return
        start = self.menu_buttons.get("start")
        if start and start.collidepoint(mx, my):
            self.start_game_with_config()

    # ==================== GAME DRAWING ====================

    def draw_board(self):
        self.screen.fill(BG_COLOR)
        for i in range(BOARD_SIZE + 1):
            x = MARGIN + i * CELL_SIZE
            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, (x, MARGIN), (x, MARGIN + BOARD_PIXEL), 1)
            pygame.draw.line(self.screen, LINE_COLOR, (MARGIN, y), (MARGIN + BOARD_PIXEL, y), 1)

        for sr, sc in STAR_POINTS:
            if sr < BOARD_SIZE and sc < BOARD_SIZE:
                px, py = self.board_to_pixel(sr, sc)
                pygame.draw.circle(self.screen, GRID_DOT_COLOR, (px, py), 4)

        for i in range(BOARD_SIZE):
            cx = MARGIN + i * CELL_SIZE + CELL_SIZE // 2
            label = self.font_coord.render(str(i), True, LINE_COLOR)
            self.screen.blit(label, (cx - label.get_width() // 2, MARGIN - 18))
            cy = MARGIN + i * CELL_SIZE + CELL_SIZE // 2
            self.screen.blit(label, (MARGIN - 22, cy - label.get_height() // 2))

    def draw_pieces(self):
        board = self.manager.board
        for row in range(board.size):
            for col in range(board.size):
                cell = board.grid[row][col]
                if cell == EMPTY:
                    continue
                x, y = self.board_to_pixel(row, col)
                if cell == PLAYER_X:
                    off = 14
                    pygame.draw.line(self.screen, X_COLOR, (x - off, y - off), (x + off, y + off), 3)
                    pygame.draw.line(self.screen, X_COLOR, (x + off, y - off), (x - off, y + off), 3)
                elif cell == PLAYER_O:
                    pygame.draw.circle(self.screen, O_COLOR, (x, y), 16, 3)

    def draw_last_move(self):
        if self.last_move is None:
            return
        row, col = self.last_move
        x, y = self.board_to_pixel(row, col)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR,
                         (x - CELL_SIZE // 2, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE), 2)

    def draw_win_line(self):
        if not self.win_cells:
            return
        for r, c in self.win_cells:
            x, y = self.board_to_pixel(r, c)
            pygame.draw.rect(self.screen, WIN_LINE_COLOR,
                             (x - CELL_SIZE // 2 + 2, y - CELL_SIZE // 2 + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                             3, border_radius=6)

    def draw_hover(self):
        if self.game_over or self.ai_thinking:
            return
        if self.game_mode == "ava":
            return
        if self.game_mode == "hva" and self.manager.current_player != PLAYER_X:
            return
        if self.hover_pos is None:
            return
        row, col = self.hover_pos
        if row is None:
            return
        if not self.manager.board.is_valid_move(row, col):
            return
        x, y = self.board_to_pixel(row, col)
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill((0, 0, 0, 40))
        self.screen.blit(s, (x - CELL_SIZE // 2, y - CELL_SIZE // 2))

    def draw_panel(self):
        panel_y = HEIGHT - PANEL_HEIGHT
        pygame.draw.rect(self.screen, PANEL_BG, (0, panel_y, WIDTH, PANEL_HEIGHT))
        pygame.draw.line(self.screen, (80, 80, 80), (0, panel_y), (WIDTH, panel_y), 2)

        mode_labels = {"hvh": "Human vs Human", "hva": "Human vs AI", "ava": "AI vs AI"}
        title = self.font_title.render(f"CARO AI — {mode_labels[self.game_mode]}", True, PANEL_ACCENT)
        self.screen.blit(title, (20, panel_y + 10))

        c1, c2 = 20, WIDTH // 2 + 10
        r1, r2, r3 = panel_y + 50, panel_y + 75, panel_y + 100

        if self.ai_config_label:
            cfg = self.font_small.render(self.ai_config_label, True, (255, 200, 80))
            self.screen.blit(cfg, (WIDTH - cfg.get_width() - 20, panel_y + 15))

        algo_text = f"Algorithm: {self.stats['algorithm'].upper()}"
        depth_text = f"Depth: {self.stats['depth']}"
        states_text = f"States: {self.stats['states']:,}"
        time_text = f"Time: {self.stats['time']:.3f}s"
        score_text = f"Score: {self.stats['score']}" if self.stats['score'] is not None else "Score: —"

        self.screen.blit(self.font_stat.render(algo_text, True, PANEL_TEXT), (c1, r1))
        self.screen.blit(self.font_stat.render(depth_text, True, PANEL_TEXT), (c1, r2))
        self.screen.blit(self.font_stat.render(states_text, True, PANEL_TEXT), (c2, r1))
        self.screen.blit(self.font_stat.render(time_text, True, PANEL_TEXT), (c2, r2))
        self.screen.blit(self.font_stat.render(score_text, True, PANEL_TEXT), (c2, r3))

        turn_text = ""
        if not self.game_over:
            if self.ai_thinking:
                turn_text = "AI thinking..."
            elif self.game_mode == "hvh":
                turn_text = f"Turn: {self.manager.current_player}"
            elif self.game_mode == "hva":
                turn_text = "Your turn (X)" if self.manager.current_player == PLAYER_X else "AI turn (O)"
            else:
                turn_text = f"AI {self.manager.current_player} turn"
        if turn_text:
            tc = (255, 200, 80) if self.ai_thinking else PANEL_ACCENT
            self.screen.blit(self.font_stat.render(turn_text, True, tc), (c1, r3))

    def draw_game_over_overlay(self):
        if not self.game_over:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        if self.winner == PLAYER_X:
            msg = "X WINS!"
            color = (100, 255, 100)
        elif self.winner == PLAYER_O:
            msg = "O WINS!"
            color = (255, 80, 80)
        else:
            msg = "DRAW!"
            color = (255, 255, 100)

        text = self.font_big.render(msg, True, color)
        self.screen.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT // 2 - 100))

        btn_w, btn_h = 200, 50
        bx = (WIDTH - btn_w) // 2

        self.restart_btn = pygame.Rect(bx, HEIGHT // 2 - 20, btn_w, btn_h)
        self.back_btn = pygame.Rect(bx, HEIGHT // 2 + 45, btn_w, btn_h)
        mx, my = pygame.mouse.get_pos()

        for btn, label in [(self.restart_btn, "Play Again"), (self.back_btn, "Back to Menu")]:
            hovered = btn.collidepoint(mx, my)
            bc = BUTTON_HOVER if hovered else BUTTON_COLOR
            pygame.draw.rect(self.screen, bc, btn, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), btn, 2, border_radius=10)
            t = self.font_btn.render(label, True, BUTTON_TEXT)
            self.screen.blit(t, (btn.x + (btn.w - t.get_width()) // 2, btn.y + (btn.h - t.get_height()) // 2))

    # ==================== GAME LOGIC ====================

    def handle_human_click(self, mx, my):
        if self.game_over or self.ai_thinking:
            return
        if self.game_mode == "ava":
            return
        if self.game_mode == "hva" and self.manager.current_player != PLAYER_X:
            return

        row, col = self.pixel_to_board(mx, my)
        if row is None:
            return
        if not self.manager.board.is_valid_move(row, col):
            return

        self.manager.board.make_move(row, col, self.manager.current_player)
        self.last_move = (row, col)

        is_over, winner = is_terminal(self.manager.board)
        if is_over:
            self.game_over = True
            self.winner = winner
            if winner:
                self.win_cells = self.get_win_cells(self.manager.board, row, col)
            return

        self.manager.switch_player()

        if self.game_mode == "hva":
            self.start_ai_turn()

    def start_ai_turn(self):
        self.ai_thinking = True
        self.ai_thread = threading.Thread(target=self.run_ai_turn, daemon=True)
        self.ai_thread.start()

    def run_ai_turn(self):
        current = self.manager.current_player
        if self.game_mode == "ava":
            ai = self.ai_x if current == PLAYER_X else self.ai_o
        else:
            ai = self.ai_o

        print(f"[AI TURN] player={current} algo={ai.algorithm} depth={ai.depth}")

        start = time.time()
        result = ai.get_move(self.manager.board)

        if isinstance(result, dict):
            row, col = result.get("row"), result.get("col")
            score, states = result.get("score"), result.get("states_explored", 0)
        elif isinstance(result, tuple) and len(result) == 2:
            row, col = result
            score, states = None, 0
        else:
            row, col = result[0], result[1]
            score, states = None, 0

        elapsed = time.time() - start
        self.manager.board.make_move(row, col, current)
        self.last_move = (row, col)
        self.stats["states"] = states
        self.stats["time"] = elapsed
        self.stats["score"] = score
        self.stats["algorithm"] = ai.algorithm
        self.stats["depth"] = ai.depth

        is_over, winner = is_terminal(self.manager.board)
        if is_over:
            self.game_over = True
            self.winner = winner
            if winner:
                self.win_cells = self.get_win_cells(self.manager.board, row, col)
            self.ai_thinking = False
            return

        self.manager.switch_player()
        self.ai_thinking = False

        if self.game_mode == "ava" and not self.game_over:
            time.sleep(0.3)
            self.start_ai_turn()

    # ==================== MAIN LOOP ====================

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if self.state == "menu":
                        self.handle_menu_click(mx, my)
                    elif self.game_over:
                        if hasattr(self, 'restart_btn') and self.restart_btn.collidepoint(mx, my):
                            self.start_game_with_config()
                        elif hasattr(self, 'back_btn') and self.back_btn.collidepoint(mx, my):
                            self.ai_thinking = False
                            self.state = "menu"
                    else:
                        self.handle_human_click(mx, my)

                if event.type == pygame.MOUSEMOTION and self.state == "playing":
                    mx, my = event.pos
                    r, c = self.pixel_to_board(mx, my)
                    self.hover_pos = (r, c) if r is not None else None

            if self.state == "menu":
                self.draw_menu()
            else:
                self.draw_board()
                self.draw_hover()
                self.draw_pieces()
                self.draw_last_move()
                self.draw_win_line()
                self.draw_panel()
                self.draw_game_over_overlay()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    game = CaroGame()
    game.run()


if __name__ == "__main__":
    main()
