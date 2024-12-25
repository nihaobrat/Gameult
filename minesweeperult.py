"""
Файл: minesweeperult.py
Описание:
    - Упрощённый "Сапёр" 10x10, полноэкранный режим, адаптируется под текущее разрешение экрана.
    - Главное меню (Начать игру / Выйти), управление стрелками + Enter.
    - Меню паузы (ESC) => (Продолжить / В главное меню), управление стрелками + Enter.
    - Сохранение количества побед в файл "minesweeperult_score.txt".
    - Сохранение лучшего времени в файл "minesweeperult_besttime.txt".
    - Медленный тёмный градиентный фон, статичный текст "PAUSED".
    - Отображение текущего времени и лучшего результата во время игры.
    - Мерцание текста при победе/поражении.
"""

import pygame
import sys
import random
import os
import math
import colorsys

# ============= ОКНО =============
pygame.init()

# Получаем текущее разрешение экрана
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# Устанавливаем полноэкранный режим
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("MinesweeperULT")
clock = pygame.time.Clock()

# ============= ЦВЕТА =============
CELL_COVERED   = (150, 150, 150)
CELL_REVEALED  = (200, 200, 200)
CELL_FLAG      = (255, 50, 50)
TEXT_COLOR     = (0, 0, 0)
BOMB_COLOR     = (255, 0, 0)
WHITE_COLOR    = (255, 255, 255)
PAUSE_OVERLAY  = (0, 0, 0, 180)  # Полупрозрачный для паузы

# ============= ШРИФТЫ =============
pygame.font.init()
font        = pygame.font.SysFont("Helvetica", 36, bold=True)
font_large  = pygame.font.SysFont("Helvetica", 80, bold=True)
font_small  = pygame.font.SysFont("Helvetica", 50, bold=True)
font_pause  = pygame.font.SysFont("Helvetica", 150, bold=True)
font_medium = pygame.font.SysFont("Helvetica", 60, bold=True)  # Добавлено определение font_medium

# ============= ПАРАМЕТРЫ ПОЛЯ САПЁРА =============
GRID_SIZE  = 10
CELL_SIZE  = 60
NUM_MINES  = 15
OFFSET_X   = (SCREEN_WIDTH  - GRID_SIZE * CELL_SIZE) // 2
OFFSET_Y   = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2

# ============= КЛАСС ЯЧЕЙКИ =============
class Cell:
    def __init__(self):
        self.is_mine     = False
        self.is_revealed = False
        self.is_flagged  = False
        self.mine_count  = 0

# Создаём поле
def create_grid():
    grid = [[Cell() for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]

    # Расставим мины
    mines_placed = 0
    while mines_placed < NUM_MINES:
        r = random.randint(0, GRID_SIZE - 1)
        c = random.randint(0, GRID_SIZE - 1)
        if not grid[r][c].is_mine:
            grid[r][c].is_mine = True
            mines_placed += 1

    # Подсчитаем соседние мины
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if not grid[row][col].is_mine:
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr = row + dr
                        nc = col + dc
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                            if grid[nr][nc].is_mine:
                                count += 1
                grid[row][col].mine_count = count

    return grid

def reveal_cell(grid, row, col):
    """Открытие ячейки. Если 0 – рекурсивно открываем соседей."""
    if grid[row][col].is_flagged or grid[row][col].is_revealed:
        return
    grid[row][col].is_revealed = True
    if grid[row][col].mine_count == 0 and not grid[row][col].is_mine:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr = row + dr
                nc = col + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if not grid[nr][nc].is_revealed and not grid[nr][nc].is_mine:
                        reveal_cell(grid, nr, nc)

def check_win(grid):
    """Победа, если все не-мины открыты."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell = grid[row][col]
            if not cell.is_mine and not cell.is_revealed:
                return False
    return True

# ============= ЗАГРУЗКА/СОХРАНЕНИЕ КОЛ-ВА ПОБЕД И ЛУЧШЕГО ВРЕМЕНИ =============
def load_wins():
    """Загружает количество побед из файла."""
    if os.path.exists("minesweeperult_score.txt"):
        with open("minesweeperult_score.txt", "r", encoding="utf-8") as f:
            try:
                wins = int(f.read().strip())
                return wins
            except:
                return 0
    else:
        return 0

def save_wins(wins):
    """Сохраняет количество побед в файл."""
    with open("minesweeperult_score.txt", "w", encoding="utf-8") as f:
        f.write(str(wins))

def load_best_time():
    """Загружает лучшее время из файла."""
    if os.path.exists("minesweeperult_besttime.txt"):
        with open("minesweeperult_besttime.txt", "r", encoding="utf-8") as f:
            try:
                best_time = float(f.read().strip())
                return best_time
            except:
                return None
    else:
        return None

def save_best_time(best_time):
    """Сохраняет лучшее время в файл."""
    with open("minesweeperult_besttime.txt", "w", encoding="utf-8") as f:
        f.write(str(best_time))

# ============= АНИМАЦИЯ ФОНА =============
animation_phase = 0

def animate_background_slowdark():
    """Медленный тёмный градиент HSV->RGB."""
    global animation_phase
    animation_phase += 0.2
    hue = (animation_phase % 360) / 360
    sat = 0.3
    val = 0.4
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return (int(r * 255), int(g * 255), int(b * 255))

def animate_text_blink(text, font_, color, center, position, phase_speed=0.005):
    """Мерцающий текст."""
    phase = math.sin(pygame.time.get_ticks() * phase_speed)
    alpha = abs(int(phase * 255))
    # Создаём поверхностный объект с альфа-каналом
    blink_surface = pygame.Surface(font_.size(text), pygame.SRCALPHA)
    blink_surface.fill((color[0], color[1], color[2], alpha))
    text_surf = font_.render(text, True, color)
    blink_surface.blit(text_surf, (0, 0))
    if center:
        rect = blink_surface.get_rect(center=position)
    else:
        rect = blink_surface.get_rect(topleft=position)
    screen.blit(blink_surface, rect)

# ============= ОТРИСОВКА ГРИДА И ЭЛЕМЕНТОВ =============
def draw_grid(grid, game_over, win, elapsed_time, best_time):
    screen.fill(animate_background_slowdark())

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = OFFSET_X + col * CELL_SIZE
            y = OFFSET_Y + row * CELL_SIZE
            cell = grid[row][col]

            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if cell.is_revealed or game_over:
                if cell.is_mine:
                    pygame.draw.rect(screen, BOMB_COLOR, rect)
                else:
                    pygame.draw.rect(screen, CELL_REVEALED, rect)
                    if cell.mine_count > 0:
                        text_surface = font.render(str(cell.mine_count), True, TEXT_COLOR)
                        screen.blit(text_surface, (x + CELL_SIZE // 3, y + CELL_SIZE // 6))
            else:
                # Закрытая клетка
                pygame.draw.rect(screen, CELL_COVERED, rect)
                if cell.is_flagged:
                    pygame.draw.rect(screen, CELL_FLAG, rect)

            pygame.draw.rect(screen, WHITE_COLOR, rect, 2)

    # Если игра окончена — выводим сообщение
    if game_over:
        msg = "Взорвались!" if not win else "Победа!"
        bottom_y = OFFSET_Y + GRID_SIZE * CELL_SIZE + 50
        if win:
            # Мерцающий текст "Победа!"
            animate_text_blink(msg, font_large, WHITE_COLOR, True, (SCREEN_WIDTH // 2, bottom_y))
        else:
            # Статичный текст "Взорвались!"
            text_surface = font_large.render(msg, True, WHITE_COLOR)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, bottom_y))
            screen.blit(text_surface, text_rect)

        # Инструкции
        lines = ["Enter - начать заново", "ESC - в меню"]
        for i, ln in enumerate(lines):
            if win:
                animate_text_blink(ln, font_small, WHITE_COLOR, True, (SCREEN_WIDTH // 2, bottom_y + 80 + i * 60))
            else:
                # Если проигрыш, сделать инструкции статичными
                text_surf = font_small.render(ln, True, WHITE_COLOR)
                rr = text_surf.get_rect(center=(SCREEN_WIDTH // 2, bottom_y + 80 + i * 60))
                screen.blit(text_surf, rr)

    # Отображение текущего времени и лучшего результата
    time_text = f"Время: {elapsed_time:.2f} сек"
    time_surf = font.render(time_text, True, WHITE_COLOR)
    screen.blit(time_surf, (OFFSET_X, OFFSET_Y - 100))

    if best_time is not None:
        best_text = f"Лучшее время: {best_time:.2f} сек"
    else:
        best_text = "Лучшее время: --"
    best_surf = font.render(best_text, True, WHITE_COLOR)
    screen.blit(best_surf, (OFFSET_X + 300, OFFSET_Y - 100))  # Смещено вправо для красоты

# ============= MENU: MAIN (Начать игру / Выйти) =============
def main_menu():
    items = ["Начать игру", "Выйти"]
    idx = 0
    while True:
        bg = animate_background_slowdark()
        screen.fill(bg)

        title_srf = font_pause.render("MinesweeperULT", True, WHITE_COLOR)
        title_rect = title_srf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_srf, title_rect)

        for i, text in enumerate(items):
            col = WHITE_COLOR
            if i == idx:
                col = (255, 0, 0)
            srf = font_medium.render(text, True, col)
            rr = srf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 80))
            screen.blit(srf, rr)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(items)
                elif event.key == pygame.K_RETURN:
                    if idx == 0:
                        return "start"
                    else:
                        pygame.quit()
                        sys.exit()

# ============= MENU: PAUSE (Продолжить / В главное меню) =============
def pause_menu():
    items = ["Продолжить", "В главное меню"]
    idx = 0
    while True:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY)
        screen.blit(overlay, (0, 0))

        # Статичный текст "PAUSED"
        paused_srf = font_pause.render("PAUSED", True, WHITE_COLOR)
        paused_rect = paused_srf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(paused_srf, paused_rect)

        for i, it in enumerate(items):
            col = WHITE_COLOR
            if i == idx:
                col = (255, 0, 0)
            srf = font_small.render(it, True, col)
            rr = srf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 80))
            screen.blit(srf, rr)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(items)
                elif event.key == pygame.K_RETURN:
                    if idx == 0:
                        return "continue"
                    else:
                        return "menu"

# ============= MAIN LOOP: Одна партия игры =============
def run_game():
    grid = create_grid()
    game_over = False
    win = False
    wins = load_wins()
    best_time = load_best_time()
    start_time = pygame.time.get_ticks()
    paused_time = 0
    pause_start_ticks = 0

    while True:
        current_ticks = pygame.time.get_ticks()
        if not game_over:
            elapsed_time = (current_ticks - start_time - paused_time) / 1000  # в секундах
        else:
            elapsed_time = (pause_start_ticks - start_time - paused_time) / 1000  # время до окончания игры

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not game_over:
                        # Записываем момент начала паузы
                        pause_start_ticks = pygame.time.get_ticks()
                        # Меню паузы
                        pm_res = pause_menu()  # "continue"/"menu"
                        if pm_res == "continue":
                            # Вычисляем, сколько времени было в паузе
                            paused_duration = pygame.time.get_ticks() - pause_start_ticks
                            paused_time += paused_duration
                        else:
                            # В главное меню
                            return
                    else:
                        # Если игра окончена, ESC возвращает в главное меню
                        return
                elif event.key == pygame.K_RETURN and game_over:
                    # Перезапуск игры
                    if win:
                        # Увеличиваем счёт побед
                        wins += 1
                        save_wins(wins)
                        # Проверяем, является ли текущее время лучшим
                        if best_time is None or elapsed_time < best_time:
                            best_time = elapsed_time
                            save_best_time(best_time)
                    # Создаём новое поле
                    grid = create_grid()
                    game_over = False
                    win = False
                    start_time = pygame.time.get_ticks()
                    paused_time = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = (mouse_x - OFFSET_X) // CELL_SIZE
                row = (mouse_y - OFFSET_Y) // CELL_SIZE
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if event.button == 1:  # левая кнопка мыши
                        if not grid[row][col].is_flagged:
                            grid[row][col].is_revealed = True
                            if grid[row][col].is_mine:
                                game_over = True
                                win = False
                            else:
                                if grid[row][col].mine_count == 0:
                                    reveal_cell(grid, row, col)
                            if check_win(grid):
                                game_over = True
                                win = True
                    elif event.button == 3:  # правая кнопка мыши
                        cell = grid[row][col]
                        if not cell.is_revealed:
                            cell.is_flagged = not cell.is_flagged

        draw_grid(grid, game_over, win, elapsed_time, best_time)

        # Отображаем количество побед
        win_text = f"Победы: {wins}"
        win_surf = font.render(win_text, True, WHITE_COLOR)
        screen.blit(win_surf, (OFFSET_X, OFFSET_Y - 150))

        pygame.display.flip()
        clock.tick(60)  # Плавность анимации

# ============= MAIN FUNCTION =============
def main():
    while True:
        # Главное меню
        mm = main_menu()  # "start"/exit
        if mm != "start":
            pygame.quit()
            sys.exit()
        # Запустить партию
        run_game()

if __name__ == "__main__":
    main()
