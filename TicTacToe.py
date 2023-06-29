import pygame
import sys, time
import numpy as np
import copy
import random
from data.constants import *
from data.button import Button
from data.animations.anim_loader import AnimationManager
# from animations.from_to_anim_loader import AnimationManager

pygame.init()

FPS = 60
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
scale = 6
scaled_display = pygame.Surface((SCREEN_WIDTH/scale, SCREEN_HEIGHT/scale)).convert()
logo_img = pygame.image.load("data/logo.png")
pygame.display.set_caption("Tic Tac Toe")
pygame.display.set_icon(logo_img)
screen.fill(BG_COLOR)

# Game Font
font = pygame.font.SysFont("calibri", SQ_SIZE, True)
O_SYMBOL = font.render("O", True, O_COLOR)
X_SYMBOL = font.render("X", True, X_COLOR)

# Animation Manager
anim_manger = AnimationManager("data/animations", (255, 0, 255))

# ============================= BOARD CLASS ================================ #
class Board:
    def __init__(self):
        self.squares = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.empty_squares = self.squares # empty sqares
        self.marked_squares = 0

    # return the game state which player is winning or the game is draw
    def final_state(self, showLine = False):
        """
            return 0 of there is no win
            return 1 if player 1 win
            return 2 if player 2 win
        """
        # verticals wins
        for col in range(BOARD_COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                # drawing line 
                if showLine:
                    color = O_COLOR if self.squares[0][col] == 1 else X_COLOR
                    pos_x = col * SQ_SIZE + (SQ_SIZE//2)
                    offset = 15
                    width = int(10/100 * SQ_SIZE) # 20% of SQ_SIZE
                    start_pos = (pos_x, offset)
                    end_pos = (pos_x, SCREEN_HEIGHT - offset)
                    pygame.draw.line(screen, color, start_pos, end_pos, width)
                return self.squares[0][col] # return the winner player number

        # horizontals wins
        for row in range(BOARD_ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                # drawing line 
                if showLine:
                    color = O_COLOR if self.squares[row][0] == 1 else X_COLOR
                    pos_y = row * SQ_SIZE + (SQ_SIZE//2)
                    offset = 15
                    width = int(10/100 * SQ_SIZE) # 20% of SQ_SIZE
                    start_pos = (offset, pos_y)
                    end_pos = (SCREEN_HEIGHT - offset, pos_y)
                    pygame.draw.line(screen, color, start_pos, end_pos, width)
                return self.squares[row][0] # return the winner player number

        # diagonal back \
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if showLine:
                color = O_COLOR if self.squares[1][1] == 1 else X_COLOR
                offset = 15
                width = int(10/100 * SQ_SIZE) # 20% of SQ_SIZE
                start_pos = (offset, offset)
                end_pos = (SCREEN_WIDTH - offset, SCREEN_HEIGHT - offset)
                pygame.draw.line(screen, color, start_pos, end_pos, width)
            return self.squares[1][1] # return the winner player number
        
        # diagonal front /
        if self.squares[0][2] == self.squares[1][1] == self.squares[2][0] != 0:
            if showLine:
                color = O_COLOR if self.squares[1][1] == 1 else X_COLOR
                offset = 15
                width = int(10/100 * SQ_SIZE) # 20% of SQ_SIZE
                start_pos = (SCREEN_WIDTH - offset, offset)
                end_pos = (offset, SCREEN_HEIGHT - offset)
                pygame.draw.line(screen, color, start_pos, end_pos, width)
            return self.squares[1][1] # return the winner player number

        return 0 # no wins

    # mark the square according to the player turn O if player is 1 else X
    def mark_square(self, row, col, player):
        self.squares[row][col] = player
        self.marked_squares += 1

    # check whether square is empty at give row, col
    def isSqEmpty(self, row, col):
        return self.squares[row][col] == 0

    # check if the board is full    
    def isFull(self):
        return self.marked_squares == 9

    # return the list of empty squares
    def get_empty_squares(self):
        empty_squares = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.isSqEmpty(row, col):
                    empty_squares.append((row, col))
        
        return empty_squares


# ============================= AI CLASS ================================= #
class AI:
    def __init__(self, level = 1, player = 2):
        self.level = level
        self.player = player
    
    def rmd_choice(self, board):
        empty_squares = board.get_empty_squares()
        idx = random.randrange(0, len(empty_squares))
        return empty_squares[idx]

    def minimax(self, board, maximizing):
        case = board.final_state()

        if case == 1:
            return 1, None
        
        if case == 2:
            return -1, None
        
        elif board.isFull():
            return 0, None
        
        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_squares()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_square(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
            
            return max_eval, best_move
        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_squares()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_square(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
            
            return min_eval, best_move

    def evaluate(self, main_board):
        if self.level == 0:
            move = self.rmd_choice(main_board)
        else:
            eval, move = self.minimax(main_board, False)
        
        print(f"Ai has choosen to mark the square in pos {move} with an eval {eval}.")
        return move


# =============================== GAME CLASS =================================== #
class Game:
    def __init__(self):
        self.board = Board()
        self.gameMode = "AI" # pvp or ai
        self.player = 1
        self.winner = None
        self.running = True
        self.drawLines()

        # For Drawing winning animation
        self.winning_anim_delay = 100 # in miliseconds
        self.winning_anim_alpha = 20
        self.o_winning_anim = anim_manger.load_animation("o_winning_anim")
        self.o_winning_anim.set_speed(0.7)
        self.x_winning_anim = anim_manger.load_animation("x_winning_anim")
        self.x_winning_anim.set_speed(0.7)
        self.draw_anim = anim_manger.load_animation("draw_anim")
        self.draw_anim.set_speed(0.6)
        self.blacked_display = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.blacked_display.fill(BG_COLOR)
        self.blacked_display.set_alpha(20)

        # Music(SFX)
        self.victory_sound = pygame.mixer.Sound("data/sfx/win_sound.wav")
        self.victory_sound.set_volume(0.3)
        self.draw_sound = pygame.mixer.Sound("data/sfx/draw_sound.wav")
        self.draw_sound.set_volume(0.3)
        self.played = 0

    # Drawing lines on board
    def drawLines(self):
        screen.fill(BG_COLOR)
        # vertical lines
        pygame.draw.line(screen, LINE_COLOR, (SQ_SIZE, 0), (SQ_SIZE, SCREEN_HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (SQ_SIZE * 2, 0), (SQ_SIZE * 2, SCREEN_HEIGHT), LINE_WIDTH)

        # horizontal lines
        pygame.draw.line(screen, LINE_COLOR, (0, SQ_SIZE), (SCREEN_WIDTH, SQ_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, SQ_SIZE * 2), (SCREEN_WIDTH, SQ_SIZE * 2), LINE_WIDTH)
    
    # Drawing symbols 'o' and 'x' according to players turn
    def drawSymbols(self, row, col):
        center_x = col * SQ_SIZE + SQ_SIZE // 2
        center_y = row * SQ_SIZE + SQ_SIZE // 2 + (7/100 * SQ_SIZE) # (7/100 * SQ_SIZE) => 7% of SQ_SIZE

        o_rect = O_SYMBOL.get_rect(center = (center_x, center_y))
        x_rect = X_SYMBOL.get_rect(center = (center_x, center_y))

        if self.player == 1:
            screen.blit(O_SYMBOL, o_rect)

        elif self.player == 2:
            screen.blit(X_SYMBOL, x_rect)

    # updating player chance
    def next_turn(self):
        self.player = self.player % 2 + 1        
                
    def isGameOver(self, board):
        return board.final_state(showLine = True) != 0 or board.isFull()
    
    # Draw Winner Screen
    def drawWinnerScreen(self):
        screen.blit(self.blacked_display, (0, 0))
        if self.winning_anim_delay <= 20:
            self.winning_anim_alpha += 5
            scaled_display.set_alpha(self.winning_anim_alpha)
            scaled_display.fill(BG_COLOR)
            if self.winner:
                if self.winner == 1:
                    self.o_winning_anim.play(1/FPS)
                    self.o_winning_anim.render_at_screen_center(scaled_display, self.o_winning_anim.img)
                elif self.winner == 2:
                    self.x_winning_anim.play(1/FPS)
                    self.x_winning_anim.render_at_screen_center(scaled_display, self.x_winning_anim.img)
                if self.played == 0:
                    self.victory_sound.play()
                    self.played += 1
            else:
                self.draw_anim.play(1/FPS)
                self.draw_anim.render_at_screen_center(scaled_display, self.draw_anim.img)
                if self.played == 0:
                    self.draw_sound.play()
                    self.played += 1
            screen.blit(pygame.transform.scale(scaled_display, screen.get_size()), (0, 0))

    # changes the gameMode from pvp to ai or ai to pvp
    def change_gameMode(self):
        self.gameMode = "AI" if self.gameMode == "PVP" else "PVP"
        print(f"Game Mode Change to {self.gameMode}.")

    # reset the game 
    def reset(self, mode):
        self.__init__()
        self.gameMode = mode


# ================= Start Screen ========================= #
def start_screen():
    scale = 4
    scaled_display = pygame.Surface((SCREEN_WIDTH/scale, SCREEN_HEIGHT/scale))
    start_screen_anim = anim_manger.load_animation("main_menu_anim")
    img = pygame.image.load("data/btn_ref.png")
    start_screen_anim.set_speed(0.5)
    pwai_button = Button(95, 316, img, scale)
    pwf_button = Button(95, 402, img, scale)
    start_screen_running = True
    while start_screen_running:
        screen.blit(pygame.transform.scale(scaled_display, screen.get_size()), (0, 0))
        scaled_display.fill(BG_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                start_screen_running = False
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # main()
                    # start_screen_running = False
                    pass
        
        start_screen_anim.render_at_screen_center(scaled_display, start_screen_anim.img)
        start_screen_anim.play(1/60)

        
        if pwai_button.draw(scaled_display):
            main("AI")
            start_screen_running = False

        if pwf_button.draw(scaled_display):
            main("PVP")
            start_screen_running = False
        
        pygame.display.update()
        clock.tick(FPS)




# ================== Main method ========================= #
def main(mode):
    game = Game()
    game.gameMode = mode
    board = Board()
    ai = AI()
    
    # Music 
    click_sound = pygame.mixer.Sound("data/sfx/click_sound.wav")

    # Game Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    game.change_gameMode()

                # Reset
                if event.key == pygame.K_r:
                    game.reset(mode)
                    board = Board()
                    ai = AI()
                # Go to menu
                elif event.key == pygame.K_BACKSPACE:
                    start_screen()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_sound.play()
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]

                    clicked_row = mouseY // SQ_SIZE
                    clicked_col = mouseX // SQ_SIZE
                    if board.isSqEmpty(clicked_row, clicked_col) and game.running:
                        board.mark_square(clicked_row, clicked_col, game.player)
                        game.drawSymbols(clicked_row, clicked_col)
                        game.next_turn()
                        # 
                        if game.isGameOver(board):
                            game.winner = board.final_state()
                            game.running = False

        if game.gameMode == "AI" and game.player == ai.player and game.running:
            pygame.display.update()

            # ai methods
            row, col = ai.evaluate(board)
            pygame.time.delay(400)
            board.mark_square(row, col, ai.player)
            click_sound.play()
            game.drawSymbols(row, col)
            game.next_turn()
            if game.isGameOver(board):
                game.winner = board.final_state()
                game.running = False
        elif not game.running:
            game.winning_anim_delay -= 1.2
            game.drawWinnerScreen()
        

            
        # updating the screen
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    start_screen()