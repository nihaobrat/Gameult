import pygame
import random
import sys
import math
import colorsys

# Инициализация Pygame
pygame.init()

# Параметры экрана
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
BACKGROUND_COLOR = (40, 0, 62)
PLAYER_COLOR = (0, 255, 0)
FONT_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
GREEN_BUTTON_COLOR = (204, 255, 204)
RED_BUTTON_COLOR = (255, 204, 204)
HOVER_GREEN_COLOR = (0, 255, 0)
HOVER_RED_COLOR = (255, 0, 0)
SHADOW_COLOR = (30, 30, 30)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("AgarioULT")
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont("Helvetica", 100, bold=True)
clock = pygame.time.Clock()

game_active = False
player_name = ""
selected_button_index = 0
border_hue = 0  # Для анимации рамки заголовка

# Функция для отображения текста
def draw_text(text, x, y, font, color=FONT_COLOR, center=False):
    text_surface = font.render(text, True, color)
    if center:
        x -= text_surface.get_width() // 2
        y -= text_surface.get_height() // 2
    screen.blit(text_surface, (x, y))

# Функция для анимированной рамки заголовка
def draw_animated_border(x, y, width, height):
    global border_hue
    rgb = colorsys.hsv_to_rgb(border_hue, 0.8, 1)
    border_color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    pygame.draw.rect(screen, border_color, (x - 15, y - 15, width + 30, height + 30), 8)
    border_hue += 0.01
    if border_hue > 1:
        border_hue = 0

# Функция начального экрана
def start_screen():
    global game_active, selected_button_index
    screen.fill(BACKGROUND_COLOR)
    buttons = [("Начать играть", GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR),
               ("Выйти", RED_BUTTON_COLOR, HOVER_RED_COLOR)]
    button_rects = [pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 60),
                    pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 60)]
    background_circles = create_circles(30, 10, 30)
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_background_circles(background_circles)

        # Отрисовка заголовка с анимированной рамкой
        title_surface = title_font.render("AgarioULT", True, (0, 255, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        draw_animated_border(title_rect.x, title_rect.y, title_rect.width, title_rect.height)
        screen.blit(title_surface, title_rect)

        for i, (text, color, hover_color) in enumerate(buttons):
            draw_button(text, button_rects[i], color, hover_color, selected=i == selected_button_index)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_button_index = (selected_button_index - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    selected_button_index = (selected_button_index + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    if selected_button_index == 0:
                        game_active = True
                        input_name_screen()
                        running = False
                    elif selected_button_index == 1:
                        pygame.quit()
                        sys.exit()

# Функция для создания кругов
def create_circles(num_circles, min_radius, max_radius):
    circles = []
    for _ in range(num_circles):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        radius = random.randint(min_radius, max_radius)
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        circles.append(Circle(x, y, radius, color))
    return circles

# Функция для анимации фоновых кругов
def draw_background_circles(circles):
    for circle in circles:
        circle.move()
        circle.draw()

# Класс игрока
class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.radius = 20
        self.base_speed = 34

    def grow(self, amount):
        self.radius += amount * 0.5
        self.base_speed = max(1, 6 - (self.radius / 50))

    def move(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        distance = math.hypot(dx, dy)
    
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            speed = min(self.base_speed, distance)
            self.x += dx * speed
            self.y += dy * speed

        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    def draw(self):
        pygame.draw.circle(screen, PLAYER_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)
        draw_text(player_name, int(self.x), int(self.y), font, center=True, color=WHITE_COLOR)

# Класс кругов для еды и врагов
class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = max(1, 6 - self.radius / 15)
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

        if self.x < -self.radius:
            self.x = SCREEN_WIDTH + self.radius
        elif self.x > SCREEN_WIDTH + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = SCREEN_HEIGHT + self.radius
        elif self.y > SCREEN_HEIGHT + self.radius:
            self.y = -self.radius

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 1)

    # Добавьте этот метод, чтобы проверить столкновение с другим объектом
    def is_colliding(self, other):
        distance = math.hypot(self.x - other.x, self.y - other.y)
        return distance < self.radius + other.radius

# Функция для экрана ввода имени
def input_name_screen():
    global player_name
    background_circles = create_circles(30, 10, 30)
    screen.fill(BACKGROUND_COLOR)
    input_active = True
    name = ""

    while input_active:
        screen.fill(BACKGROUND_COLOR)
        draw_background_circles(background_circles)
        
        draw_text("Введите ваш ник:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120, font, center=True, color=WHITE_COLOR)
        draw_text(name, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, font, center=True, color=WHITE_COLOR)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    player_name = name
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

# Функция паузы
def pause_menu():
    global selected_button_index
    paused = True
    buttons = [("Продолжить", GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR),
               ("Выйти в меню", RED_BUTTON_COLOR, HOVER_RED_COLOR)]
    button_rects = [pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 50),
                    pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 50)]
    selected_button_index = 0

    while paused:
        screen.fill(BACKGROUND_COLOR)
        
        for i, (text, color, hover_color) in enumerate(buttons):
            draw_button(text, button_rects[i], color, hover_color, selected=i == selected_button_index)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_button_index = (selected_button_index - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    selected_button_index = (selected_button_index + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    if selected_button_index == 0:
                        paused = False
                    elif event.key == pygame.K_RETURN:
                        pygame.quit()
                        sys.exit()

# Основная функция игры
def main():
    global game_active
    player = Player()
    food_circles = create_circles(50, 5, 15)
    enemy_circles = create_circles(15, 20, 50)
    
    score = 0
    new_circle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(new_circle_timer, 3000)

    while game_active:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu()
            elif event.type == new_circle_timer:
                food_circles.extend(create_circles(10, 5, 15))
                enemy_circles.extend(create_circles(3, 20, 50))

        player.move()

        for food in food_circles[:]:
            if food.is_colliding(player):
                player.grow(food.radius // 4)
                food_circles.remove(food)
                score += 1

        for enemy in enemy_circles[:]:
            enemy.move()
            if enemy.is_colliding(player):
                if player.radius > enemy.radius:
                    player.grow(enemy.radius // 4)
                    enemy_circles.remove(enemy)
                    score += 5
                else:
                    game_over_screen(score)
                    game_active = False
                    break

            for other_enemy in enemy_circles:
                if other_enemy != enemy and enemy.is_colliding(other_enemy):
                    if enemy.radius > other_enemy.radius:
                        enemy.radius += other_enemy.radius // 4
                        enemy_circles.remove(other_enemy)

        player.draw()
        for food in food_circles:
            food.draw()
        for enemy in enemy_circles:
            enemy.draw()

        draw_text(f"Score: {score}", 10, 10, font, color=WHITE_COLOR)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

# Функция экрана завершения игры
def game_over_screen(score):
    global selected_button_index
    screen.fill(BACKGROUND_COLOR)
    draw_text(f"Ваш итоговый результат: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, font, center=True, color=WHITE_COLOR)

    buttons = [("Начать заново", GREEN_BUTTON_COLOR, HOVER_GREEN_COLOR),
               ("Выйти", RED_BUTTON_COLOR, HOVER_RED_COLOR)]
    button_rects = [pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 60),
                    pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 60)]
    selected_button_index = 0

    waiting = True
    while waiting:
        for i, (text, color, hover_color) in enumerate(buttons):
            draw_button(text, button_rects[i], color, hover_color, selected=i == selected_button_index)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_button_index = (selected_button_index - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    selected_button_index = (selected_button_index + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    if selected_button_index == 0:
                        waiting = False
                        main()
                    elif selected_button_index == 1:
                        pygame.quit()
                        sys.exit()

# Функция для отрисовки кнопок с тенью и черным текстом
def draw_button(text, rect, color, hover_color, selected=False):
    color_to_use = hover_color if selected else color
    shadow_offset = 4
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=10)
    pygame.draw.rect(screen, color_to_use, rect, border_radius=10)
    draw_text(text, rect.centerx, rect.centery, font, center=True, color=FONT_COLOR)

# Запуск игры
if __name__ == "__main__":
    start_screen()
    if game_active:
        main()
