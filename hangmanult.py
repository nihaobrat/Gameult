import pygame
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Получение текущих размеров экрана для полноэкранного режима
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)  # Полноэкранный режим
pygame.display.set_caption("HangmanULT")
clock = pygame.time.Clock()

# Определение цветов
TEXT_COLOR = (255, 255, 255)
GREEN_BUTTON_COLOR = (0, 200, 0)
RED_BUTTON_COLOR = (200, 0, 0)
HOVER_GREEN_COLOR = (0, 255, 0)
HOVER_RED_COLOR = (255, 0, 0)
WORD_COLOR = (255, 255, 255)
HANGMAN_COLOR = (255, 0, 0)
GALLOWS_COLOR = (255, 255, 255)
SHADOW_COLOR = (30, 30, 30)
BACKGROUND_COLOR = (40, 0, 62)

# Список слов
WORDS = ["АБСТРАКЦИЯ", "АДАПТАЦИЯ", "АКАДЕМИЯ", "АКТИВНОСТЬ", "АЛГОРИТМ", "АЛЬТЕРНАТИВА", "АНАЛИЗ", "АНАТОМИЯ"]

# Шрифты
font_large = pygame.font.SysFont("Helvetica", 100, bold=True)
font = pygame.font.SysFont(None, 48)

# Параметры игры
MAX_MISSES = 10
HANGMAN_PART_DURATION = 500  # Продолжительность анимации для каждой части виселицы (в миллисекундах)

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
        self.reset_game_state()

    def start_two_player(self, word):
        self.set_word(word)
        self.mode = "game"
        self.input_mode = False
        self.input_text = ""
        self.reset_game_state()

    def reset_game_state(self):
        self.misses = 0
        self.word_revealed = False
        self.word_guessed = False
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
            if self.misses < MAX_MISSES:
                self.part_draw_times[self.misses] = pygame.time.get_ticks()
                self.misses += 1
                if self.misses >= MAX_MISSES:
                    pygame.time.delay(500)
                    self.word_revealed = True
                    self.end_time = time.time()
                    self.game_over = True

    def draw_game(self):
        screen.fill(BACKGROUND_COLOR)
        self.draw_word()
        self.draw_hangman()
        self.draw_timer()

        if self.word_revealed:
            self.draw_loss_message()
        elif self.word_guessed:
            self.draw_win_message()

    def draw_main_menu(self):
        screen.fill(BACKGROUND_COLOR)
        self.draw_title("HangmanULT", CENTER_X, 100)

        # Определение кнопок относительно центра
        button_width = 200
        button_height = 60
        button_spacing = 100  # Расстояние между кнопками

        # Кнопка "Играть"
        play_button_rect = pygame.Rect(0, 0, button_width, button_height)
        play_button_rect.center = (CENTER_X, CENTER_Y - button_spacing // 2)

        # Кнопка "Выйти"
        exit_button_rect = pygame.Rect(0, 0, button_width, button_height)
        exit_button_rect.center = (CENTER_X, CENTER_Y + button_spacing // 2)

        draw_button("Играть", play_button_rect, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Выйти", exit_button_rect, RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 1)

    def draw_mode_selection(self):
        screen.fill(BACKGROUND_COLOR)
        self.draw_title("Выберите режим", CENTER_X, 100)

        # Определение кнопок относительно центра
        button_width = 200
        button_height = 60
        button_spacing = 100  # Расстояние между кнопками

        # Кнопка "1 Игрок"
        one_player_rect = pygame.Rect(0, 0, button_width, button_height)
        one_player_rect.center = (CENTER_X, CENTER_Y - button_spacing)

        # Кнопка "2 Игрока"
        two_player_rect = pygame.Rect(0, 0, button_width, button_height)
        two_player_rect.center = (CENTER_X, CENTER_Y)

        # Кнопка "Назад"
        back_rect = pygame.Rect(0, 0, button_width, button_height)
        back_rect.center = (CENTER_X, CENTER_Y + button_spacing)

        draw_button("1 Игрок", one_player_rect, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("2 Игрока", two_player_rect, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 1)
        draw_button("Назад", back_rect, RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 2)

    def draw_title(self, text, x, y):
        shadow_offset = 4
        shadow_color = SHADOW_COLOR

        title_surface = font_large.render(text, True, (0, 255, 0))
        shadow_surface = font_large.render(text, True, shadow_color)

        # Центрирование заголовка
        screen.blit(shadow_surface, (x - shadow_surface.get_width() // 2 + shadow_offset, y + shadow_offset))
        screen.blit(title_surface, (x - title_surface.get_width() // 2, y))

    def draw_word_entry(self):
        screen.fill(BACKGROUND_COLOR)
        # Текст запроса слова
        prompt_text = "Игрок 1: придумайте слово"
        draw_text_center(prompt_text, CENTER_X, CENTER_Y - 100)
        draw_text_center(self.input_text, CENTER_X, CENTER_Y - 50)

        # Определение кнопок относительно центра
        button_width = 200
        button_height = 60
        button_spacing = 80  # Расстояние между кнопками

        # Кнопка "Загадать"
        set_word_rect = pygame.Rect(0, 0, button_width, button_height)
        set_word_rect.center = (CENTER_X, CENTER_Y + 30)

        # Кнопка "Назад"
        back_rect = pygame.Rect(0, 0, button_width, button_height)
        back_rect.center = (CENTER_X, CENTER_Y + 30 + button_spacing)

        draw_button("Загадать", set_word_rect, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Назад", back_rect, RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 1)

    def draw_word(self):
        word_display = " ".join(self.guessed_letters)
        word_surface = font.render(word_display, True, WORD_COLOR)
        word_rect = word_surface.get_rect(center=(CENTER_X, CENTER_Y - 200))
        screen.blit(word_surface, word_rect)

    def draw_timer(self):
        if self.game_over and self.end_time:
            elapsed_time = int(self.end_time - self.start_time)
        else:
            elapsed_time = int(time.time() - self.start_time)
        timer_text = f"Время в игре: {elapsed_time} сек"
        timer_surface = font.render(timer_text, True, TEXT_COLOR)
        timer_rect = timer_surface.get_rect(center=(CENTER_X, CENTER_Y + 250))
        screen.blit(timer_surface, timer_rect)

    def draw_hangman(self):
        current_time = pygame.time.get_ticks()
        center_x = CENTER_X
        center_y = CENTER_Y  # Основная точка для рисования виселицы

        # Параметры виселицы
        base_length = 300
        upright_height = 300
        top_beam_length = 150
        noose_length = 50

        # Определяем координаты частей виселицы относительно центра
        base_start = (center_x - base_length // 2, center_y + upright_height // 2)
        base_end = (center_x + base_length // 2, center_y + upright_height // 2)

        upright_start = base_start
        upright_end = (center_x - base_length // 2, center_y - upright_height // 2)

        top_beam_start = upright_end
        top_beam_end = (upright_end[0] + top_beam_length, upright_end[1])

        noose_start = top_beam_end
        noose_end = (noose_start[0], noose_start[1] + noose_length)

        gallows_parts = [
            (base_start, base_end),            # Основание
            (upright_start, upright_end),      # Вертикальная часть
            (top_beam_start, top_beam_end),    # Верхняя балка
            (noose_start, noose_end)           # Петля
        ]

        hangman_parts = [
            # Определяем функции для рисования частей человечка
            lambda: pygame.draw.circle(screen, HANGMAN_COLOR, (center_x, noose_end[1] + 20), 20, 5),  # Голова
            lambda: pygame.draw.line(screen, HANGMAN_COLOR, (center_x, noose_end[1] + 40),
                                     (center_x, noose_end[1] + 120), 8),  # Тело
            lambda: pygame.draw.line(screen, HANGMAN_COLOR, (center_x, noose_end[1] + 60),
                                     (center_x - 30, noose_end[1] + 90), 5),  # Левая рука
            lambda: pygame.draw.line(screen, HANGMAN_COLOR, (center_x, noose_end[1] + 60),
                                     (center_x + 30, noose_end[1] + 90), 5),  # Правая рука
            lambda: pygame.draw.line(screen, HANGMAN_COLOR, (center_x, noose_end[1] + 120),
                                     (center_x - 30, noose_end[1] + 170), 5),  # Левая нога
            lambda: pygame.draw.line(screen, HANGMAN_COLOR, (center_x, noose_end[1] + 120),
                                     (center_x + 30, noose_end[1] + 170), 5)   # Правая нога
        ]

        # Рисуем виселицу
        for i in range(min(self.misses, 4)):
            if self.part_draw_times[i] and current_time >= self.part_draw_times[i]:
                start_pos, end_pos = gallows_parts[i]
                progress = min((current_time - self.part_draw_times[i]) / HANGMAN_PART_DURATION, 1)
                draw_end_pos = (
                    start_pos[0] + progress * (end_pos[0] - start_pos[0]),
                    start_pos[1] + progress * (end_pos[1] - start_pos[1])
                )
                pygame.draw.line(screen, GALLOWS_COLOR, start_pos, draw_end_pos, 8)

        # Рисуем человечка
        for i in range(4, self.misses):
            if self.part_draw_times[i] and current_time >= self.part_draw_times[i]:
                progress = min((current_time - self.part_draw_times[i]) / HANGMAN_PART_DURATION, 1)
                if i - 4 < len(hangman_parts):
                    # Для анимации можно добавить прогресс, но для простоты рисуем сразу
                    hangman_parts[i - 4]()

        # Опционально: Отладочные линии для проверки центрирования (уберите после проверки)
        # pygame.draw.line(screen, (255, 255, 0), (CENTER_X, 0), (CENTER_X, SCREEN_HEIGHT), 1)  # Вертикальная
        # pygame.draw.line(screen, (255, 255, 0), (0, CENTER_Y), (SCREEN_WIDTH, CENTER_Y), 1)    # Горизонтальная

    def draw_loss_message(self):
        loss_message = f"Игра завершена! Было загадано слово: {self.word}"
        restart_message = "Для продолжения нажмите Enter"
        loss_surface = font.render(loss_message, True, TEXT_COLOR)
        restart_surface = font.render(restart_message, True, TEXT_COLOR)

        # Располагаем сообщение ближе к верхней части экрана
        # Определяем отступы относительно верхнего края
        loss_y = 150  # Расстояние от верхнего края
        restart_y = 220  # Расстояние от верхнего края

        loss_rect = loss_surface.get_rect(center=(CENTER_X, loss_y))
        restart_rect = restart_surface.get_rect(center=(CENTER_X, restart_y))

        screen.blit(loss_surface, loss_rect)
        screen.blit(restart_surface, restart_rect)

    def draw_win_message(self):
        win_message = "Поздравляем! Повешения не будет!"
        restart_message = "Для продолжения нажмите Enter"
        win_surface = font.render(win_message, True, TEXT_COLOR)
        restart_surface = font.render(restart_message, True, TEXT_COLOR)

        # Располагаем сообщение ближе к верхней части экрана
        # Определяем отступы относительно верхнего края
        win_y = 150  # Расстояние от верхнего края
        restart_y = 220  # Расстояние от верхнего края

        win_rect = win_surface.get_rect(center=(CENTER_X, win_y))
        restart_rect = restart_surface.get_rect(center=(CENTER_X, restart_y))

        screen.blit(win_surface, win_rect)
        screen.blit(restart_surface, restart_rect)

def draw_text(text, x, y, color=TEXT_COLOR, center=False):
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, (x, y))

def draw_text_center(text, x, y, color=TEXT_COLOR):
    draw_text(text, x, y, color, center=True)

def draw_button(text, rect, color, hover_color, selected):
    color_to_use = hover_color if selected else color
    shadow_offset = 4
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=10)
    pygame.draw.rect(screen, color_to_use, rect, border_radius=10)
    draw_text_center(text, rect.centerx, rect.centery)

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
                elif game.mode == "game":
                    if not game.game_over:
                        if event.key == pygame.K_ESCAPE:
                            game.mode = "menu"
                        elif event.unicode.isalpha():
                            game.guess_letter(event.unicode)
                    else:
                        if event.key == pygame.K_RETURN:
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
