import pygame
import random
import sys
import colorsys

# Инициализация Pygame
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CELL_SIZE = 20
SCREEN_COLOR = (40, 0, 62)
SNAKE_HEAD_COLOR = (0, 128, 0)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
GREEN_BUTTON_COLOR = (204, 255, 204)
RED_BUTTON_COLOR = (255, 204, 204)
HOVER_GREEN_COLOR = (0, 255, 0)
HOVER_RED_COLOR = (255, 0, 0)
SHADOW_COLOR = (30, 30, 30)
BORDER_COLOR = (200, 200, 200)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("SnakeULT")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 36, bold=True)
title_font = pygame.font.SysFont("Helvetica", 100, bold=True)  # Новый шрифт для заголовка

# Параметры для анимации рамки и текста
border_hue = 0

# Функция для отображения текста
def draw_text(text, x, y, font, color=TEXT_COLOR, center=False):
    text_surface = font.render(text, True, color)
    if center:
        x = x - text_surface.get_width() // 2
        y = y - text_surface.get_height() // 2
    screen.blit(text_surface, (x, y))

# Функция для создания анимированной рамки вокруг текста заголовка
def draw_animated_border(x, y, width, height):
    global border_hue
    rgb = colorsys.hsv_to_rgb(border_hue, 0.8, 1)
    border_color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    pygame.draw.rect(screen, border_color, (x - 15, y - 15, width + 30, height + 30), 8)
    border_hue += 0.01
    if border_hue > 1:
        border_hue = 0

# Основной класс игры
class SnakeGame:
    def __init__(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = (CELL_SIZE, 0)
        self.food = None
        self.score = 0
        self.high_scores = {"Easy": 0, "Medium": 0, "Hard": 0}
        self.load_high_scores()
        self.game_over = False
        self.in_menu = True
        self.in_level_select = False
        self.in_pause = False
        self.selected_option = 0
        self.selected_difficulty = "Easy"
        self.walls = []
        self.super_speed = False
        self.setup_level(self.selected_difficulty)

    def load_high_scores(self):
        try:
            with open("high_scores.txt", "r") as f:
                for line in f:
                    level, score = line.strip().split(":")
                    self.high_scores[level] = int(score)
        except FileNotFoundError:
            self.high_scores = {"Easy": 0, "Medium": 0, "Hard": 0}

    def save_high_scores(self):
        with open("high_scores.txt", "w") as f:
            for level, score in self.high_scores.items():
                f.write(f"{level}:{score}\n")

    def setup_level(self, difficulty):
        if difficulty == "Easy":
            self.speed = 10
            self.walls = []
        elif difficulty == "Medium":
            self.speed = 12
            self.walls = [pygame.Rect(random.randint(2, SCREEN_WIDTH // CELL_SIZE - 4) * CELL_SIZE,
                                      random.randint(2, SCREEN_HEIGHT // CELL_SIZE - 4) * CELL_SIZE,
                                      CELL_SIZE * 2, CELL_SIZE) for _ in range(5)]
        elif difficulty == "Hard":
            self.speed = 15
            self.walls = [pygame.Rect(random.randint(2, SCREEN_WIDTH // CELL_SIZE - 4) * CELL_SIZE,
                                      random.randint(2, SCREEN_HEIGHT // CELL_SIZE - 4) * CELL_SIZE,
                                      CELL_SIZE * 2, CELL_SIZE) for _ in range(15)]
        self.food = new_food_position(self.walls)

    def start_game(self):
        self.in_level_select = False
        self.in_pause = False
        self.game_over = False
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = (CELL_SIZE, 0)
        self.food = new_food_position(self.walls)
        self.score = 0
        self.super_speed = False
        self.setup_level(self.selected_difficulty)

    def update(self):
        if self.game_over or self.in_menu or self.in_level_select or self.in_pause:
            return

        new_head = (
            self.snake[0][0] + self.direction[0],
            self.snake[0][1] + self.direction[1],
        )

        if (new_head[0] < CELL_SIZE or new_head[0] >= SCREEN_WIDTH - CELL_SIZE or
            new_head[1] < CELL_SIZE or new_head[1] >= SCREEN_HEIGHT - CELL_SIZE or
            new_head in self.snake or any(wall.collidepoint(new_head) for wall in self.walls)):
            self.game_over = True
            if self.score > self.high_scores[self.selected_difficulty]:
                self.high_scores[self.selected_difficulty] = self.score
                self.save_high_scores()
            self.selected_option = 0
            return

        self.snake = [new_head] + self.snake[:-1]

        if new_head == self.food:
            self.snake.append(self.snake[-1])
            self.food = new_food_position(self.walls)
            self.score += 1

            if self.selected_difficulty in ["Medium", "Hard"] and self.score % 5 == 0:
                self.add_walls(2)

    def add_walls(self, count):
        added_walls = 0
        attempts = 0
        max_attempts = 100

        while added_walls < count and attempts < max_attempts:
            new_wall = pygame.Rect(
                random.randint(2, (SCREEN_WIDTH // CELL_SIZE - 4)) * CELL_SIZE,
                random.randint(2, (SCREEN_HEIGHT // CELL_SIZE - 4)) * CELL_SIZE,
                CELL_SIZE * 2, CELL_SIZE
            )
            if (new_wall.collidelist(self.walls) == -1 and 
                all(segment != (new_wall.x, new_wall.y) for segment in self.snake) and 
                not new_wall.colliderect(pygame.Rect(*self.food, CELL_SIZE, CELL_SIZE))):
                self.walls.append(new_wall)
                added_walls += 1
            attempts += 1

    def change_direction(self, direction):
        opposite_direction = (-self.direction[0], -self.direction[1])
        if direction != opposite_direction:
            self.direction = direction

    def draw(self):
        screen.fill(SCREEN_COLOR)
        if self.in_menu:
            self.draw_main_menu()
        elif self.in_level_select:
            self.draw_level_select()
        elif self.game_over:
            self.draw_game_over_screen()
        elif self.in_pause:
            self.draw_pause_menu()
        else:
            self.draw_game()

    def draw_game(self):
        draw_border()
        for wall in self.walls:
            pygame.draw.rect(screen, BORDER_COLOR, wall)
        for i, segment in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            pygame.draw.rect(screen, color, (*segment, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, FOOD_COLOR, (*self.food, CELL_SIZE, CELL_SIZE))
        draw_text(f"Счёт: {self.score}", CELL_SIZE + 10, CELL_SIZE + 10, font)
        draw_text(f"Рекорд: {self.high_scores[self.selected_difficulty]}", SCREEN_WIDTH - 180, CELL_SIZE + 10, font)

    def draw_main_menu(self):
        animate_snakes()
        title_surface = title_font.render("SnakeULT", True, (0, 255, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        draw_animated_border(title_rect.x, title_rect.y, title_rect.width, title_rect.height)
        screen.blit(title_surface, title_rect)

        start_game_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 60)
        exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 60)
        draw_button("Начать игру", start_game_button, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Выйти", exit_button, RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 1)

    def draw_level_select(self):
        animate_snakes()
        draw_text("Выберите уровень сложности", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, font, center=True)
        easy_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 80, 200, 50)
        medium_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        hard_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 50)
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 160, 200, 50)
        draw_button("Простой", easy_button, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Средний", medium_button, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 1)
        draw_button("Сложный", hard_button, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 2)
        draw_button("Назад", back_button, RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 3)

    def draw_pause_menu(self):
        draw_text("Пауза", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, font, center=True)
        continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 220, 60)
        main_menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 220, 60)
        draw_button("Продолжить", continue_button, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Выйти в меню", main_menu_button, RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 1)

    def draw_game_over_screen(self):
        draw_text(f"Ваш счёт: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, font, center=True)
        draw_text(f"Лучший результат: {self.high_scores[self.selected_difficulty]}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 40, font, center=True)
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 220, 50)
        main_menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 220, 50)
        draw_button("Начать заново", restart_button, GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR, self.selected_option == 0)
        draw_button("Выйти в меню", main_menu_button, RED_BUTTON_COLOR, HOVER_RED_COLOR, self.selected_option == 1)

# Функция для создания объемной кнопки с тенью
def draw_button(text, rect, color, hover_color, selected):
    button_color = hover_color if selected else color
    shadow_offset = 5  # Смещение тени

    # Рисуем тень
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=10)

    # Рисуем основную кнопку
    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=10)  # Черная рамка вокруг кнопки

    # Отображаем текст в центре кнопки
    draw_text(text, rect.centerx, rect.centery, font, color="black", center=True)

# Функция для создания границ игрового поля
def draw_border():
    pygame.draw.rect(screen, BORDER_COLOR, (CELL_SIZE, CELL_SIZE, SCREEN_WIDTH - 2 * CELL_SIZE, SCREEN_HEIGHT - 2 * CELL_SIZE), 2)

# Анимация змей на фоне
def animate_snakes():
    for snake in snakes:
        head_x, head_y = snake['segments'][0]
        new_head_x = head_x + snake['dx']
        new_head_y = head_y + snake['dy']

        # Обновляем положение сегментов змейки
        snake['segments'] = [(new_head_x, new_head_y)] + snake['segments'][:-1]

        # Отражение от стен
        if new_head_x < 0 or new_head_x > SCREEN_WIDTH:
            snake['dx'] *= -1
        if new_head_y < 0 or new_head_y > SCREEN_HEIGHT:
            snake['dy'] *= -1

        # Рисуем сегменты змейки
        for i, (x, y) in enumerate(snake['segments']):
            color = (max(0, 255 - i * 15), max(0, 255 - i * 20), random.randint(100, 255))
            pygame.draw.circle(screen, color, (int(x), int(y)), snake['radius'])

# Функция для генерации новой еды, избегая стены
def new_food_position(walls):
    while True:
        food_position = (
            random.randint(2, (SCREEN_WIDTH - 2 * CELL_SIZE) // CELL_SIZE - 1) * CELL_SIZE,
            random.randint(2, (SCREEN_HEIGHT - 2 * CELL_SIZE) // CELL_SIZE - 1) * CELL_SIZE,
        )
        if all(not wall.collidepoint(food_position) for wall in walls):
            return food_position

# Инициализация змей для анимации
num_snakes = 15
snake_speed = 8
snakes = []
for _ in range(num_snakes):
    segments = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(10)]
    dx = random.choice([-snake_speed, snake_speed])
    dy = random.choice([-snake_speed, snake_speed])
    snakes.append({
        'segments': segments,
        'dx': dx,
        'dy': dy,
        'radius': 10
    })

def main():
    game = SnakeGame()
    super_speed = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game.in_menu:
                    if event.key == pygame.K_UP:
                        game.selected_option = (game.selected_option - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        game.selected_option = (game.selected_option + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if game.selected_option == 0:
                            game.in_menu = False
                            game.in_level_select = True
                            game.selected_option = 0
                        elif game.selected_option == 1:
                            pygame.quit()
                            sys.exit()
                elif game.in_level_select:
                    if event.key == pygame.K_UP:
                        game.selected_option = (game.selected_option - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        game.selected_option = (game.selected_option + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if game.selected_option == 3:
                            game.in_level_select = False
                            game.in_menu = True
                            game.selected_option = 0
                        else:
                            levels = ["Easy", "Medium", "Hard"]
                            game.selected_difficulty = levels[game.selected_option]
                            game.start_game()
                elif game.in_pause:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        game.selected_option = (game.selected_option + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if game.selected_option == 0:
                            game.in_pause = False
                        elif game.selected_option == 1:
                            game.in_menu = True
                            game.in_pause = False
                            game.selected_option = 0
                elif game.game_over:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        game.selected_option = (game.selected_option + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if game.selected_option == 0:
                            game.start_game()
                        elif game.selected_option == 1:
                            game.in_menu = True
                            game.game_over = False
                            game.selected_option = 0
                else:
                    if event.key == pygame.K_UP:
                        game.change_direction((0, -CELL_SIZE))
                    elif event.key == pygame.K_DOWN:
                        game.change_direction((0, CELL_SIZE))
                    elif event.key == pygame.K_LEFT:
                        game.change_direction((-CELL_SIZE, 0))
                    elif event.key == pygame.K_RIGHT:
                        game.change_direction((CELL_SIZE, 0))
                    elif event.key == pygame.K_RETURN:
                        super_speed = True
                    elif event.key == pygame.K_ESCAPE:
                        game.in_pause = True
                        game.selected_option = 0
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    super_speed = False

        game.update()
        game.draw()

        if super_speed:
            clock.tick(game.speed * 2)
        else:
            clock.tick(game.speed + game.score // 5)

        pygame.display.flip()

if __name__ == "__main__":
    main()
