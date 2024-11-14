import pygame
import sys
import random
import time

# Screen parameters and colors
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TEXT_COLOR = (255, 255, 255)
GREEN_BUTTON_COLOR = (0, 200, 0)
RED_BUTTON_COLOR = (200, 0, 0)
HOVER_GREEN_COLOR = (0, 255, 0)
HOVER_RED_COLOR = (255, 0, 0)
WORD_COLOR = (255, 255, 255)
HANGMAN_COLOR = (255, 0, 0)
GALLOWS_COLOR = (255, 255, 255)
SHADOW_COLOR = (30, 30, 30)

# Word list
WORDS = ["АБСТРАКЦИЯ", "АДАПТАЦИЯ", "АКАДЕМИЯ", "АКТИВНОСТЬ", "АЛГОРИТМ", "АЛЬТЕРНАТИВА", "АНАЛИЗ", "АНАТОМИЯ"]

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)  # Fullscreen mode
pygame.display.set_caption("HangmanULT")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

# Game parameters
MAX_MISSES = 10
HANGMAN_PART_DURATION = 500  # Duration for each hangman part drawing (in ms)

class HangmanGame:
    def __init__(self):
        self.reset_game()
        self.mode = "menu"
        self.selected_option = 0
        self.input_text = ""
        self.input_mode = False

    def reset_game(self):
        self.word = ""
        self.guessed_letters = []
        self.misses = 0
        self.start_time = None
        self.end_time = None
        self.game_over = False
        self.word_revealed = False
        self.word_guessed = False
        self.part_draw_times = [None] * MAX_MISSES

    def set_word(self, word):
        self.word = word.upper()
        self.guessed_letters = ["_"] * len(word)
        self.start_time = time.time()

    def start_single_player(self):
        self.set_word(random.choice(WORDS))
        self.mode = "game"
        self.misses = 0
        self.word_revealed = False
        self.word_guessed = False
        self.part_draw_times = [None] * MAX_MISSES
        self.end_time = None

    def start_two_player(self, word):
        self.set_word(word)
        self.mode = "game"
        self.input_mode = False
        self.input_text = ""
        self.part_draw_times = [None] * MAX_MISSES
        self.end_time = None

    def guess_letter(self, letter):
        if self.game_over or letter in self.guessed_letters:
            return
        letter = letter.upper()
        if letter in self.word:
            for i, char in enumerate(self.word):
                if char == letter:
                    self.guessed_letters[i] = letter
            if "_" not in self.guessed_letters:
                self.word_guessed = True
                self.end_time = time.time()
                self.game_over = True
        else:
            self.part_draw_times[self.misses] = pygame.time.get_ticks()
            self.misses += 1
            if self.misses >= MAX_MISSES:
                pygame.time.delay(500)
                self.word_revealed = True
                self.end_time = time.time()
                self.game_over = True

    def draw_game(self):
        screen.fill((40, 0, 62))
        self.draw_word()
        self.draw_hangman()
        self.draw_timer()
        
        if self.word_revealed:
            self.draw_loss_message()
        elif self.word_guessed:
            self.draw_win_message()

    def draw_main_menu(self):
        screen.fill((40, 0, 62))
        self.draw_title("HangmanULT", SCREEN_WIDTH // 2, 100)
        draw_button("Играть", pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 60),
                    GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Выйти", pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 60),
                    RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 1)

    def draw_mode_selection(self):
        screen.fill((40, 0, 62))
        self.draw_title("HangmanULT", SCREEN_WIDTH // 2, 100)
        draw_button("1 Игрок", pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 60),
                    GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("2 Игрока", pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 60),
                    GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 1)
        draw_button("Назад", pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 60),
                    RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 2)

    def draw_title(self, text, x, y):
        shadow_offset = 4
        shadow_color = (30, 30, 30)
        
        font_large = pygame.font.SysFont("Helvetica", 100, bold=True)
        title_surface = font_large.render(text, True, (0, 255, 0))
        shadow_surface = font_large.render(text, True, shadow_color)

        screen.blit(shadow_surface, (x - shadow_surface.get_width() // 2 + shadow_offset, y + shadow_offset))
        screen.blit(title_surface, (x - title_surface.get_width() // 2, y))

    def draw_word_entry(self):
        screen.fill((40, 0, 62))
        draw_text("Игрок 1: придумайте слово", SCREEN_WIDTH // 2, 250, center=True)
        draw_text(self.input_text, SCREEN_WIDTH // 2, 350, center=True)
        draw_button("Загадать", pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60),
                    GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Назад", pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 60),
                    RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 1)

    def draw_word(self):
        word_surface = font.render(" ".join(self.guessed_letters), True, WORD_COLOR)
        screen.blit(word_surface, (SCREEN_WIDTH // 2 - word_surface.get_width() // 2, 100))

    def draw_timer(self):
        if self.game_over and self.end_time:
            elapsed_time = int(self.end_time - self.start_time)
        else:
            elapsed_time = int(time.time() - self.start_time)
        timer_surface = font.render(f"Время в игре: {elapsed_time} сек", True, TEXT_COLOR)
        screen.blit(timer_surface, (SCREEN_WIDTH - 1250, 670))

    def draw_hangman(self):
        current_time = pygame.time.get_ticks()
        gallows_parts = [
            ((SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 150), (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 + 150)),
            ((SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 150), (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150)),
            ((SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)),
            ((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        ]

        hangman_parts = [
            (lambda: pygame.draw.circle(screen, HANGMAN_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 75), 20, 5)),
            (lambda: pygame.draw.line(screen, HANGMAN_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 55), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), 8)),
            (lambda: pygame.draw.line(screen, HANGMAN_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30), 5)),
            (lambda: pygame.draw.line(screen, HANGMAN_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 - 30), 5)),
            (lambda: pygame.draw.line(screen, HANGMAN_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 90), 5)),
            (lambda: pygame.draw.line(screen, HANGMAN_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), (SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 90), 5))
        ]

        for i in range(min(self.misses, 4)):
            if self.part_draw_times[i] and current_time >= self.part_draw_times[i]:
                start_pos, end_pos = gallows_parts[i]
                progress = min((current_time - self.part_draw_times[i]) / HANGMAN_PART_DURATION, 1)
                draw_end_pos = (
                    start_pos[0] + progress * (end_pos[0] - start_pos[0]),
                    start_pos[1] + progress * (end_pos[1] - start_pos[1])
                )
                pygame.draw.line(screen, GALLOWS_COLOR, start_pos, draw_end_pos, 8)

        for i in range(4, self.misses):
            if self.part_draw_times[i] and current_time >= self.part_draw_times[i]:
                progress = min((current_time - self.part_draw_times[i]) / HANGMAN_PART_DURATION, 1)
                if i == 4:
                    pygame.draw.circle(screen, HANGMAN_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 75), int(20 * progress), 5)
                else:
                    hangman_parts[i - 4]()

    def draw_loss_message(self):
        loss_message = f"Игра завершена! Было загадано слово: {self.word}"
        restart_message = "Для продолжения нажмите Enter"
        loss_surface = font.render(loss_message, True, TEXT_COLOR)
        restart_surface = font.render(restart_message, True, TEXT_COLOR)
        screen.blit(loss_surface, (SCREEN_WIDTH // 2 - loss_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 160))
        screen.blit(restart_surface, (SCREEN_WIDTH // 2 - restart_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 200))

    def draw_win_message(self):
        win_message = "Поздравляем! Повешения не будет!"
        restart_message = "Для продолжения нажмите Enter"
        win_surface = font.render(win_message, True, TEXT_COLOR)
        restart_surface = font.render(restart_message, True, TEXT_COLOR)
        screen.blit(win_surface, (SCREEN_WIDTH // 2 - win_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 160))
        screen.blit(restart_surface, (SCREEN_WIDTH // 2 - restart_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 200))

def draw_text(text, x, y, color=TEXT_COLOR, center=False):
    text_surface = font.render(text, True, color)
    if center:
        x = x - text_surface.get_width() // 2
        y = y - text_surface.get_height() // 2
    screen.blit(text_surface, (x, y))

def draw_button(text, rect, color, hover_color, selected):
    color_to_use = hover_color if selected else color
    shadow_offset = 4
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=10)
    pygame.draw.rect(screen, color_to_use, rect, border_radius=10)
    draw_text(text, rect.centerx, rect.centery, center=True)

def main():
    game = HangmanGame()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game.mode == "menu":
                    if event.key in [pygame.K_UP, pygame.K_DOWN]:
                        game.selected_option = (game.selected_option + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if game.selected_option == 0:
                            game.mode = "mode_selection"
                        elif game.selected_option == 1:
                            pygame.quit()
                            sys.exit()
                elif game.mode == "mode_selection":
                    if event.key in [pygame.K_UP, pygame.K_DOWN]:
                        game.selected_option = (game.selected_option + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if game.selected_option == 0:
                            game.start_single_player()
                        elif game.selected_option == 1:
                            game.input_mode = True
                            game.mode = "word_entry"
                        elif game.selected_option == 2:
                            game.mode = "menu"
                elif game.mode == "word_entry":
                    if event.key in [pygame.K_UP, pygame.K_DOWN]:
                        game.selected_option = (game.selected_option + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if game.selected_option == 0 and game.input_text:
                            game.start_two_player(game.input_text)
                        elif game.selected_option == 1:
                            game.mode = "mode_selection"
                    elif event.key == pygame.K_BACKSPACE:
                        game.input_text = game.input_text[:-1]
                    elif event.unicode.isalpha():
                        game.input_text += event.unicode.upper()
                elif game.mode == "game" and not game.game_over:
                    if event.key == pygame.K_ESCAPE:
                        game.mode = "menu"
                    elif event.unicode.isalpha():
                        game.guess_letter(event.unicode)
                elif game.game_over and event.key == pygame.K_RETURN:
                    game.reset_game()
                    game.mode = "menu"

        if game.mode == "menu":
            game.draw_main_menu()
        elif game.mode == "mode_selection":
            game.draw_mode_selection()
        elif game.mode == "word_entry":
            game.draw_word_entry()
        elif game.mode == "game":
            game.draw_game()

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
