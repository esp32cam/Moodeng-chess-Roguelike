
import pygame
import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import math
import random

# กำหนดประเภทของหมาก
class PieceType(Enum):
    PAWN = "PAWN"
    KNIGHT = "KNIGHT"
    BISHOP = "BISHOP"
    ROOK = "ROOK"
    QUEEN = "QUEEN"

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Piece:
    piece_type: PieceType
    position: Position

# @dataclass
# class Player:
#     position: Position
#     hp: int
#     abilities: List[str]

class PlayerAbilities(Enum):
    EXTRA_MOVE = "Double Move"  # เดินได้ 2 ครั้ง
    SHIELD = "Shield"          # โล่ป้องกัน 1 ครั้ง
    TELEPORT = "Teleport"      # เคลื่อนที่ข้ามฝั่งได้
    HEAL = "Heal"             # ฟื้นฟู HP 1 หน่วย
    
@dataclass
class Player:
    position: Position
    hp: int
    abilities: List[PlayerAbilities]
    shield_active: bool = False
    moves_remaining: int = 1

    def add_ability(self, ability: PlayerAbilities):
        """เพิ่มความสามารถให้ผู้เล่น"""
        self.abilities.append(ability)

    def use_ability(self, ability: PlayerAbilities) -> bool:
        """ใช้ความสามารถ"""
        if ability in self.abilities:
            if ability == PlayerAbilities.EXTRA_MOVE:
                self.moves_remaining = 2
            elif ability == PlayerAbilities.SHIELD:
                self.shield_active = True
            elif ability == PlayerAbilities.HEAL:
                self.hp = min(self.hp + 1, 5)
            self.abilities.remove(ability)
            return True
        return False

class ChessAI:
    def __init__(self, board_size: int = 8):
        self.board_size = board_size
        self.difficulty_level = 1

    def get_moves(self, piece: Piece) -> List[Position]:
        """คำนวณการเดินที่เป็นไปได้ของหมากแต่ละตัว"""
        moves = []
        
        if piece.piece_type == PieceType.PAWN:
            # เดินหน้า 1 ช่อง และแนวทแยง
            possible_moves = [
                (0, 1),   # เดินหน้า
                (1, 1),   # ทแยงขวา
                (-1, 1),  # ทแยงซ้าย
            ]
            for dx, dy in possible_moves:
                new_x = piece.position.x + dx
                new_y = piece.position.y + dy
                if self._is_valid_position(new_x, new_y):
                    moves.append(Position(new_x, new_y))
            
        elif piece.piece_type == PieceType.KNIGHT:
            knight_moves = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)
            ]
            for dx, dy in knight_moves:
                new_x = piece.position.x + dx
                new_y = piece.position.y + dy
                if self._is_valid_position(new_x, new_y):
                    moves.append(Position(new_x, new_y))
                    
        elif piece.piece_type == PieceType.ROOK:
            # เดินแนวตั้งและแนวนอน
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in directions:
                new_x = piece.position.x + dx
                new_y = piece.position.y + dy
                if self._is_valid_position(new_x, new_y):
                    moves.append(Position(new_x, new_y))
        
        return moves

    def _is_valid_position(self, x: int, y: int) -> bool:
        """ตรวจสอบว่าตำแหน่งอยู่ในกระดานหรือไม่"""
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def choose_moves(self, pieces: List[Piece], player: Player) -> List[Position]:
        """เลือกการเดินที่ดีที่สุดสำหรับ AI ทั้ง 3 ตัว"""
        moves = []
        roles = ["blocker", "attacker", "supporter"]
        
        for piece, role in zip(pieces, roles):
            possible_moves = self.get_moves(piece)
            if not possible_moves:  # ถ้าไม่มีที่ให้เดิน ให้อยู่ที่เดิม
                moves.append(piece.position)
                continue
                
            best_move = piece.position  # ถ้าไม่มีที่ดีกว่า ให้อยู่ที่เดิม
            best_score = float('-inf')
            
            for move in possible_moves:
                score = self._evaluate_move(piece, move, player, role)
                if score > best_score:
                    best_score = score
                    best_move = move
            
            moves.append(best_move)
            
        return moves

    def _evaluate_move(self, piece: Piece, move: Position, player: Player, role: str) -> float:
        """ประเมินคะแนนของการเดิน"""
        score = 0.0
        
        # ระยะห่างจากผู้เล่น
        distance = math.sqrt((move.x - player.position.x)**2 + 
                           (move.y - player.position.y)**2)
        
        # คะแนนพื้นฐานตามบทบาท
        if role == "blocker":
            # ต้องการอยู่ใกล้ผู้เล่นแต่ไม่ต้องเข้าไปติด
            score = 20 - distance if distance > 2 else 10
        elif role == "attacker":
            # ต้องการเข้าใกล้ผู้เล่นมากที่สุด
            score = 30 - distance
        else:  # supporter
            # พยายามอยู่ห่างพอประมาณและควบคุมพื้นที่
            ideal_distance = 3
            score = 20 - abs(distance - ideal_distance)

        # โบนัสถ้าสามารถกินผู้เล่นได้
        if move.x == player.position.x and move.y == player.position.y:
            score += 100

        # หักคะแนนถ้าเดินชิดขอบเกินไป
        if move.x in [0, 7] or move.y in [0, 7]:
            score -= 5

        return score
    
class Level:
    def __init__(self, level_number: int):
        self.level_number = level_number
        self.ai_setups = {
            1: [ # ด่าน 1 - เริ่มต้น
                (PieceType.PAWN, Position(1, 1)),
                (PieceType.KNIGHT, Position(3, 1)),
                (PieceType.ROOK, Position(6, 1))
            ],
            2: [ # ด่าน 2 - เพิ่มความยาก
                (PieceType.PAWN, Position(1, 1)),
                (PieceType.KNIGHT, Position(3, 1)),
                (PieceType.ROOK, Position(6, 1)),
                (PieceType.BISHOP, Position(4, 1))
            ],
            3: [ # ด่าน 3 - ปานกลาง
                (PieceType.KNIGHT, Position(2, 1)),
                (PieceType.BISHOP, Position(3, 1)),
                (PieceType.ROOK, Position(5, 1)),
                (PieceType.QUEEN, Position(4, 1)),
                (PieceType.PAWN, Position(1, 2))
            ],
            4: [ # ด่าน 4 - ยาก
                (PieceType.QUEEN, Position(4, 1)),
                (PieceType.BISHOP, Position(3, 1)),
                (PieceType.BISHOP, Position(5, 1)),
                (PieceType.KNIGHT, Position(2, 1)),
                (PieceType.KNIGHT, Position(6, 1)),
                (PieceType.PAWN, Position(4, 2))
            ],
            5: [ # ด่าน 5 - ท้าทาย
                (PieceType.QUEEN, Position(4, 1)),
                (PieceType.ROOK, Position(1, 1)),
                (PieceType.ROOK, Position(7, 1)),
                (PieceType.BISHOP, Position(3, 1)),
                (PieceType.BISHOP, Position(5, 1)),
                (PieceType.KNIGHT, Position(2, 2)),
                (PieceType.KNIGHT, Position(6, 2))
            ]
        }

    def get_ai_pieces(self) -> List[Piece]:
        """สร้างหมาก AI สำหรับด่านปัจจุบัน"""
        if self.level_number not in self.ai_setups:
            return []
        
        pieces = []
        for piece_type, position in self.ai_setups[self.level_number]:
            pieces.append(Piece(piece_type, position))
        return pieces

    def get_difficulty(self) -> int:
        """คำนวณความยากของด่าน"""
        return min(5, self.level_number)

class GameVisualizer:
    def __init__(self, window_size: int = 800):
        pygame.init()
        self.window_size = window_size
        self.square_size = window_size // 8
        self.screen = pygame.display.set_mode((window_size, window_size + 60))  # เพิ่มพื้นที่สำหรับปุ่ม
        pygame.display.set_caption("Chess AI Test Game")
        
        self.colors = {
            'white': (255, 255, 255),
            'gray': (128, 128, 128),
            'black': (0, 0, 0),
            'player': (0, 0, 255),
            'ai': (255, 0, 0),
            'valid_move': (0, 255, 0),
            'button': (50, 200, 50),  # สีปุ่ม
            'button_hover': (100, 255, 100)  # สีปุ่มเมื่อเมาส์ชี้
        }

        # กำหนดขนาดและตำแหน่งปุ่ม
        self.button_rect = pygame.Rect(
            self.window_size // 2 - 60,  # x
            self.window_size + 10,       # y
            120,                         # width
            40                          # height
        )

    def draw_button(self, mouse_pos):
        # เปลี่ยนสีปุ่มเมื่อเมาส์ชี้
        color = self.colors['button_hover'] if self.button_rect.collidepoint(mouse_pos) else self.colors['button']
        
        # วาดปุ่ม
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=5)
        
        # วาดข้อความบนปุ่ม
        font = pygame.font.Font(None, 36)
        text = font.render("Restart", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.button_rect.center)
        self.screen.blit(text, text_rect)

    def is_button_clicked(self, mouse_pos):
        return self.button_rect.collidepoint(mouse_pos)

    def draw_board(self):
        for y in range(8):
            for x in range(8):
                color = self.colors['white'] if (x + y) % 2 == 0 else self.colors['gray']
                pygame.draw.rect(self.screen, color, 
                               (x * self.square_size, y * self.square_size, 
                                self.square_size, self.square_size))

    def draw_piece(self, position: Position, piece_type: str, is_player: bool):
        x = position.x * self.square_size + self.square_size // 2
        y = position.y * self.square_size + self.square_size // 2
        color = self.colors['player'] if is_player else self.colors['ai']
        
        pygame.draw.circle(self.screen, color, (x, y), self.square_size // 3)
        
        font = pygame.font.Font(None, 36)
        text = font.render(piece_type, True, self.colors['white'])
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)

    def draw_valid_moves(self, valid_moves: List[Position]):
        for move in valid_moves:
            x = move.x * self.square_size + self.square_size // 2
            y = move.y * self.square_size + self.square_size // 2
            pygame.draw.circle(self.screen, self.colors['valid_move'], 
                             (x, y), self.square_size // 4)

    def get_square_from_mouse(self, pos) -> Position:
        x = pos[0] // self.square_size
        y = pos[1] // self.square_size
        return Position(x, y)

# class Game:
#     def __init__(self):
#         self.visualizer = GameVisualizer()
#         self.ai = ChessAI()
#         self.reset_game()

#     def reset_game(self):
#         self.player = Player(Position(4, 7), hp=3, abilities=[])
#         self.ai_pieces = [
#             Piece(PieceType.PAWN, Position(1, 1)),
#             Piece(PieceType.KNIGHT, Position(3, 1)),
#             Piece(PieceType.ROOK, Position(6, 1))
#         ]
#         self.selected = False
#         self.valid_moves = []

#     def get_player_valid_moves(self) -> List[Position]:
#         moves = []
#         for dx in [-1, 0, 1]:
#             for dy in [-1, 0, 1]:
#                 if dx == 0 and dy == 0:
#                     continue
#                 new_x = self.player.position.x + dx
#                 new_y = self.player.position.y + dy
#                 if 0 <= new_x < 8 and 0 <= new_y < 8:
#                     moves.append(Position(new_x, new_y))
#         return moves

#     def run(self):
#         running = True
#         while running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#                 elif event.type == pygame.MOUSEBUTTONDOWN:
#                     if event.button == 1:  # คลิกซ้าย
#                         clicked_pos = self.visualizer.get_square_from_mouse(event.pos)
                        
#                         if not self.selected:
#                             if clicked_pos.x == self.player.position.x and clicked_pos.y == self.player.position.y:
#                                 self.selected = True
#                                 self.valid_moves = self.get_player_valid_moves()
#                         else:
#                             move_made = False
#                             for valid_move in self.valid_moves:
#                                 if clicked_pos.x == valid_move.x and clicked_pos.y == valid_move.y:
#                                     self.player.position = clicked_pos
#                                     move_made = True
#                                     break
                            
#                             if move_made:
#                                 ai_moves = self.ai.choose_moves(self.ai_pieces, self.player)
#                                 for piece, move in zip(self.ai_pieces, ai_moves):
#                                     if move:
#                                         piece.position = move
#                                         if move.x == self.player.position.x and move.y == self.player.position.y:
#                                             self.player.hp -= 1
#                                             if self.player.hp <= 0:
#                                                 print("Game Over!")
#                                                 running = False
#                                             else:
#                                                 self.player.position = Position(4, 7)
                            
#                             self.selected = False
#                             self.valid_moves = []

#             # วาดกราฟิก
#             self.visualizer.draw_board()
#             if self.selected:
#                 self.visualizer.draw_valid_moves(self.valid_moves)
            
#             self.visualizer.draw_piece(self.player.position, "P", True)
            
#             for piece in self.ai_pieces:
#                 self.visualizer.draw_piece(piece.position, piece.piece_type.name[0], False)
            
#             font = pygame.font.Font(None, 36)
#             hp_text = font.render(f"HP: {self.player.hp}", True, (0, 0, 0))
#             self.visualizer.screen.blit(hp_text, (10, 10))
            
#             pygame.display.flip()

#         pygame.quit()

# [โค้ดส่วนอื่นๆ เหมือนเดิม แก้ไขเฉพาะ class Game]



class Game:
    def __init__(self):
        self.visualizer = GameVisualizer()
        self.ai = ChessAI()
        self.current_level = 1
        self.level_system = Level(self.current_level)
        self.player = None
        self.ai_pieces = []
        self.selected = False
        self.valid_moves = []
        self.score = 0
        self.game_over = False
        self.victory = False
        self.ability_selected = None
        self.level_complete = False  # เพิ่มตัวแปรเช็คจบด่าน
        self.reset_game()
    def draw_abilities(self):
        start_y = 130
        font = pygame.font.Font(None, 24)
        for i, ability in enumerate(self.player.abilities):
            ability_rect = pygame.Rect(10, start_y + i*40, 100, 30)
            color = (100, 200, 100) if self.ability_selected == ability else (100, 100, 200)
            pygame.draw.rect(self.visualizer.screen, color, ability_rect)
            text = font.render(ability.value, True, (255, 255, 255))
            self.visualizer.screen.blit(text, (15, start_y + i*40 + 5))
    def handle_ability_click(self, pos):
        start_y = 130
        for i, ability in enumerate(self.player.abilities):
            ability_rect = pygame.Rect(10, start_y + i*40, 100, 30)
            if ability_rect.collidepoint(pos):
                if self.ability_selected == ability:
                    self.ability_selected = None
                else:
                    self.ability_selected = ability
                return True
        return False

    def reset_game(self):
        # สร้างผู้เล่นพร้อมความสามารถเริ่มต้น
        self.player = Player(
            position=Position(4, 7),
            hp=3,
            abilities=[PlayerAbilities.SHIELD],
            shield_active=False,
            moves_remaining=1
        )
        self.current_level = 1
        self.level_system = Level(self.current_level)
        self.ai_pieces = self.level_system.get_ai_pieces()
        self.selected = False
        self.valid_moves = []
        self.score = 0
        self.game_over = False
        self.victory = False
        self.ability_selected = None
        self.level_complete = False

    def next_level(self):
        """เปลี่ยนด่านใหม่"""
        self.current_level += 1
        if self.current_level <= 5:
            print(f"\nStarting Level {self.current_level}!")
            # ให้ความสามารถใหม่
            random_ability = random.choice([
                PlayerAbilities.EXTRA_MOVE,
                PlayerAbilities.SHIELD,
                PlayerAbilities.TELEPORT,
                PlayerAbilities.HEAL
            ])
            self.player.add_ability(random_ability)
            print(f"Got new ability: {random_ability.value}!")
            
            # เตรียมด่านใหม่
            self.level_system = Level(self.current_level)
            self.player.position = Position(4, 7)
            self.ai_pieces = self.level_system.get_ai_pieces()
            
            # ให้รางวัล
            self.score += 500
            self.player.hp = min(self.player.hp + 1, 5)  # เพิ่ม HP (ไม่เกิน 5)
            
            # รีเซ็ตสถานะ
            self.level_complete = False
            self.selected = False
            self.valid_moves = []
        else:
            self.victory = True
            self.game_over = True
            print("Congratulations! You've completed all levels!")

    def check_level_complete(self):
        """ตรวจสอบว่าจบด่านหรือยัง"""
        if len(self.ai_pieces) == 0 and not self.level_complete:
            self.level_complete = True
            print(f"Level {self.current_level} Complete!")
            self.next_level()
    def handle_move(self, clicked_pos):
        if self.ability_selected == PlayerAbilities.TELEPORT:
            if 0 <= clicked_pos.x < 8 and 0 <= clicked_pos.y < 8:
                self.player.position = clicked_pos
                self.player.use_ability(PlayerAbilities.TELEPORT)
                return True
                
        for valid_move in self.valid_moves:
            if clicked_pos.x == valid_move.x and clicked_pos.y == valid_move.y:
                captured = False
                for piece in self.ai_pieces[:]:
                    if piece.position.x == clicked_pos.x and piece.position.y == clicked_pos.y:
                        self.ai_pieces.remove(piece)
                        self.score += 100
                        captured = True
                        break
                
                self.player.position = clicked_pos
                self.player.moves_remaining -= 1
                
                if self.player.moves_remaining <= 0:
                    return True
        return False
    def get_player_valid_moves(self) -> List[Position]:
        moves = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dx, dy in directions:
            new_x = self.player.position.x + dx
            new_y = self.player.position.y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                moves.append(Position(new_x, new_y))
        return moves
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # คลิกซ้าย
                        # เช็คการคลิกปุ่ม Restart
                        if self.visualizer.is_button_clicked(mouse_pos):
                            self.reset_game()
                            continue

                        if not self.game_over and not self.level_complete:
                            clicked_pos = self.visualizer.get_square_from_mouse(event.pos)
                            
                            # จัดการการคลิกความสามารถ
                            if self.handle_ability_click(event.pos):
                                continue
                                
                            if not self.selected:
                                if clicked_pos.x == self.player.position.x and clicked_pos.y == self.player.position.y:
                                    self.selected = True
                                    self.valid_moves = self.get_player_valid_moves()
                            else:
                                if self.handle_move(clicked_pos):
                                    # AI's turn
                                    ai_moves = self.ai.choose_moves(self.ai_pieces, self.player)
                                    for piece, move in zip(self.ai_pieces, ai_moves):
                                        if move:
                                            piece.position = move
                                            if move.x == self.player.position.x and move.y == self.player.position.y:
                                                if self.player.shield_active:
                                                    self.player.shield_active = False
                                                    print("Shield blocked the attack!")
                                                else:
                                                    self.player.hp -= 1
                                                    print(f"Player hit! HP: {self.player.hp}")
                                                    if self.player.hp <= 0:
                                                        print("Game Over!")
                                                        self.game_over = True
                                                    else:
                                                        self.player.position = Position(4, 7)
                                    
                                    self.player.moves_remaining = 1
                                    if self.ability_selected == PlayerAbilities.EXTRA_MOVE:
                                        self.player.use_ability(PlayerAbilities.EXTRA_MOVE)
                                
                                self.selected = False
                                self.valid_moves = []
                                
                                # เช็คว่าจบด่านหรือยัง
                                self.check_level_complete()

            # วาดกราฟิก
            self.visualizer.screen.fill((255, 255, 255))
            self.visualizer.draw_board()
            if self.selected:
                self.visualizer.draw_valid_moves(self.valid_moves)
            
            self.visualizer.draw_piece(self.player.position, "P", True)
            
            for piece in self.ai_pieces:
                self.visualizer.draw_piece(piece.position, piece.piece_type.name[0], False)
            
            # แสดงข้อมูลผู้เล่น
            font = pygame.font.Font(None, 36)
            hp_text = font.render(f"HP: {self.player.hp}", True, (0, 0, 0))
            score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
            level_text = font.render(f"Level: {self.current_level}/5", True, (0, 0, 0))
            
            self.visualizer.screen.blit(hp_text, (10, 10))
            self.visualizer.screen.blit(score_text, (10, 50))
            self.visualizer.screen.blit(level_text, (10, 90))
            
            # วาดปุ่มความสามารถ
            self.draw_abilities()
            
            # วาดปุ่ม Restart
            self.visualizer.draw_button(mouse_pos)
            
            # แสดงข้อความเมื่อจบเกม
            if self.game_over:
                if self.victory:
                    message = "Victory! All levels completed!"
                    color = (0, 255, 0)  # สีเขียว
                else:
                    message = "Game Over! Click Restart to try again"
                    color = (255, 0, 0)  # สีแดง
                game_over_text = font.render(message, True, color)
                text_rect = game_over_text.get_rect(center=(self.visualizer.window_size // 2, self.visualizer.window_size // 2))
                self.visualizer.screen.blit(game_over_text, text_rect)
            
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
