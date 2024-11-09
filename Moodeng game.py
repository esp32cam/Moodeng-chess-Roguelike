import pygame
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_SIZE // BOARD_SIZE
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class PieceType(Enum):
    PLAYER = "P"
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"

class Piece:
    def __init__(self, piece_type, x, y, is_player=False):
        self.type = piece_type
        self.x = x
        self.y = y
        self.is_player = is_player

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Chess Demo")
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.player = None
        self.ai_pieces = []
        self.player_hp = 3
        self.selected = False
        self.valid_moves = []
        self.reset_game()

    def reset_game(self):
        # Clear board
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.ai_pieces = []

        # Set player
        self.player = Piece(PieceType.PLAYER, 4, 7, True)
        self.board[self.player.y][self.player.x] = self.player

        # Set AI pieces (simplified setup)
        ai_setups = [
            (PieceType.PAWN, 1, 1),
            (PieceType.KNIGHT, 3, 1),
            (PieceType.ROOK, 6, 1)
        ]
        
        for piece_type, x, y in ai_setups:
            piece = Piece(piece_type, x, y)
            self.ai_pieces.append(piece)
            self.board[y][x] = piece

    def get_valid_moves(self, piece):
        moves = []
        if piece.is_player:  # Player moves like a king
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    new_x = piece.x + dx
                    new_y = piece.y + dy
                    if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
                        moves.append((new_x, new_y))
        return moves

    def draw_board(self):
        self.screen.fill(WHITE)
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(self.screen, GRAY,
                                  (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece = self.board[y][x]
                if piece:
                    color = BLUE if piece.is_player else RED
                    pygame.draw.circle(self.screen, color,
                                    (x * SQUARE_SIZE + SQUARE_SIZE//2,
                                     y * SQUARE_SIZE + SQUARE_SIZE//2),
                                    SQUARE_SIZE//3)

    def draw_valid_moves(self):
        for x, y in self.valid_moves:
            pygame.draw.circle(self.screen, GREEN,
                            (x * SQUARE_SIZE + SQUARE_SIZE//2,
                             y * SQUARE_SIZE + SQUARE_SIZE//2),
                            SQUARE_SIZE//8)

    def ai_move(self):
        # Simplified AI movement - random valid moves
        for piece in self.ai_pieces:
            possible_moves = []
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x = piece.x + dx
                    new_y = piece.y + dy
                    if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
                        possible_moves.append((new_x, new_y))
            
            if possible_moves:
                new_x, new_y = random.choice(possible_moves)
                self.board[piece.y][piece.x] = None
                piece.x, piece.y = new_x, new_y
                self.board[new_y][new_x] = piece

                # Check if AI captured player
                if self.player.x == new_x and self.player.y == new_y:
                    self.player_hp -= 1
                    if self.player_hp <= 0:
                        print("Game Over!")
                        return True
                    # Respawn player at random safe location
                    self.respawn_player()
        return False

    def respawn_player(self):
        safe_spots = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] is None:
                    is_safe = True
                    for piece in self.ai_pieces:
                        if abs(piece.x - x) <= 1 and abs(piece.y - y) <= 1:
                            is_safe = False
                            break
                    if is_safe:
                        safe_spots.append((x, y))
        
        if safe_spots:
            new_x, new_y = random.choice(safe_spots)
            self.board[self.player.y][self.player.x] = None
            self.player.x, self.player.y = new_x, new_y
            self.board[new_y][new_x] = self.player

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        x = event.pos[0] // SQUARE_SIZE
                        y = event.pos[1] // SQUARE_SIZE
                        
                        if not self.selected:
                            if self.board[y][x] == self.player:
                                self.selected = True
                                self.valid_moves = self.get_valid_moves(self.player)
                        else:
                            if (x, y) in self.valid_moves:
                                # Move player
                                self.board[self.player.y][self.player.x] = None
                                self.player.x, self.player.y = x, y
                                self.board[y][x] = self.player
                                self.selected = False
                                self.valid_moves = []
                                
                                # AI turn
                                game_over = self.ai_move()
                                if game_over:
                                    running = False
                            self.selected = False
                            self.valid_moves = []

            self.draw_board()
            if self.selected:
                self.draw_valid_moves()
            self.draw_pieces()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()