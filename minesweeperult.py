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
GREEN_COLOR    = (0, 255, 0)      # Новый цвет для авто-открытых клеток

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
        self.mine_count  = 0
        self.auto_opened = False  # Существующий флаг
        self.mark        = None     # Новый флаг: 'flag', 'cross', 'check'

# ============= ФУНКЦИИ =============

# Создаём поле с возможностью исключения определённых клеток из размещения мин
def create_grid(exclude_cells=None):
    if exclude_cells is None:
        exclude_cells = []
    grid = [[Cell() for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]

    # Расставим мины, исключая указанные клетки
    mines_placed = 0
    while mines_placed < NUM_MINES:
        r = random.randint(0, GRID_SIZE - 1)
        c = random.randint(0, GRID_SIZE - 1)
        if not grid[r][c].is_mine and (r, c) not in exclude_cells:
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
    if grid[row][col].is_revealed or grid[row][col].mark == 'flag':
        return
    grid[row][col].is_revealed = True
    grid[row][col].mark = None  # Сброс отметки при открытии
    if grid[row][col].mine_count == 0 and not grid[row][col].is_mine:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr = row + dr
                nc = col + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    neighbor = grid[nr][nc]
                    if not neighbor.is_revealed and not neighbor.is_mine:
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

# ============= ФУНКЦИЯ АВТО-ОТКРЫТИЯ БЕЗОПАСНЫХ КЛЕТОК =============
def auto_reveal_safe_cells(grid):
    """Автоматически открывает клетки, которые, по логике, безопасны."""
    changed = True
    while changed:
        changed = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = grid[row][col]
                if cell.is_revealed and cell.mine_count > 0:
                    flagged = 0
                    covered = []
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr = row + dr
                            nc = col + dc
                            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                                neighbor = grid[nr][nc]
                                if neighbor.mark == 'flag':
                                    flagged += 1
                                elif not neighbor.is_revealed:
                                    covered.append((nr, nc))
                    # Если количество флагов равно числу мин, оставшиеся клетки безопасны
                    if flagged == cell.mine_count:
                        for nr, nc in covered:
                            neighbor = grid[nr][nc]
                            if not neighbor.is_revealed:
                                neighbor.is_revealed = True
                                neighbor.auto_opened = True
                                if neighbor.mine_count == 0:
                                    reveal_cell(grid, nr, nc)
                                changed = True
                    # Дополнительная логика может быть добавлена здесь
    return

# ============= ФУНКЦИИ ДЛЯ РИСОВАНИЯ МЕТКИЙ =============

def draw_flag(x, y):
    """Рисует флаг на клетке."""
    # Рисуем треугольник флага
    point1 = (x + CELL_SIZE // 4, y + CELL_SIZE // 4)
    point2 = (x + CELL_SIZE // 4, y + 3 * CELL_SIZE // 4)
    point3 = (x + 3 * CELL_SIZE // 4, y + CELL_SIZE // 2)
    pygame.draw.polygon(screen, (255, 0, 0), [point1, point2, point3])

def draw_cross(x, y):
    """Рисует красный крест на клетке."""
    pygame.draw.line(screen, (255, 0, 0), (x + 10, y + 10), (x + CELL_SIZE - 10, y + CELL_SIZE - 10), 3)
    pygame.draw.line(screen, (255, 0, 0), (x + CELL_SIZE - 10, y + 10), (x + 10, y + CELL_SIZE - 10), 3)

def draw_check(x, y):
    """Рисует зеленую галочку на клетке."""
    pygame.draw.line(screen, (0, 255, 0), (x + 10, y + CELL_SIZE // 2), (x + CELL_SIZE // 3, y + CELL_SIZE - 10), 3)
    pygame.draw.line(screen, (0, 255, 0), (x + CELL_SIZE // 3, y + CELL_SIZE - 10), (x + CELL_SIZE - 10, y + 10), 3)

def cycle_mark(cell):
    """Циклически переключает маркировку клетки."""
    if cell.mark is None:
        cell.mark = 'flag'
    elif cell.mark == 'flag':
        cell.mark = 'cross'
    elif cell.mark == 'cross':
        cell.mark = 'check'
    elif cell.mark == 'check':
        cell.mark = None

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
                    color = CELL_REVEALED
                    if cell.auto_opened:
                        color = GREEN_COLOR
                    pygame.draw.rect(screen, color, rect)
                    if cell.mine_count > 0:
                        text_surface = font.render(str(cell.mine_count), True, TEXT_COLOR)
                        text_rect = text_surface.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                        screen.blit(text_surface, text_rect)
            else:
                # Закрытая клетка
                pygame.draw.rect(screen, CELL_COVERED, rect)
                # Рисуем маркировку, если есть
                if cell.mark is not None:
                    if cell.mark == 'flag':
                        draw_flag(x, y)
                    elif cell.mark == 'cross':
                        draw_cross(x, y)
                    elif cell.mark == 'check':
                        draw_check(x, y)

            # Рисуем границу клетки
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
    grid = None  # Изначально поле не создано
    game_over = False
    win = False
    wins = load_wins()
    best_time = load_best_time()
    start_time = 0
    paused_time = 0
    pause_start_ticks = 0
    first_click = True  # Флаг первого клика

    while True:
        current_ticks = pygame.time.get_ticks()
        if not game_over and not first_click:
            elapsed_time = (current_ticks - start_time - paused_time) / 1000  # в секундах
        elif not game_over and first_click:
            elapsed_time = 0
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
                    grid = None
                    game_over = False
                    win = False
                    start_time = 0
                    paused_time = 0
                    pause_start_ticks = 0
                    first_click = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = (mouse_x - OFFSET_X) // CELL_SIZE
                row = (mouse_y - OFFSET_Y) // CELL_SIZE
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if event.button == 1:  # левая кнопка мыши
                        if grid is None:
                            # Первый клик: создаём поле, исключая первую клетку и её соседей
                            exclude = [(row, col)]
                            for dr in [-1, 0, 1]:
                                for dc in [-1, 0, 1]:
                                    nr = row + dr
                                    nc = col + dc
                                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                                        exclude.append((nr, nc))
                            grid = create_grid(exclude)
                            start_time = pygame.time.get_ticks()
                            first_click = False

                        cell = grid[row][col]
                        if cell.mark != 'flag' and cell.mark != 'cross' and cell.mark != 'check':
                            reveal_cell(grid, row, col)
                            if cell.is_mine:
                                game_over = True
                                win = False
                            else:
                                if check_win(grid):
                                    game_over = True
                                    win = True
                                else:
                                    # После ручного открытия, попробуем авто-открыть безопасные клетки
                                    auto_reveal_safe_cells(grid)
                                    if check_win(grid):
                                        game_over = True
                                        win = True
                    elif event.button == 3:  # правая кнопка мыши
                        if grid is not None:
                            cell = grid[row][col]
                            if not cell.is_revealed:
                                cycle_mark(cell)

        # Отрисовка
        if grid is not None:
            draw_grid(grid, game_over, win, elapsed_time, best_time)
        else:
            # Рисуем закрытые клетки без марок (пока поле не создано)
            screen.fill(animate_background_slowdark())
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    x = OFFSET_X + col * CELL_SIZE
                    y = OFFSET_Y + row * CELL_SIZE
                    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, CELL_COVERED, rect)
                    pygame.draw.rect(screen, WHITE_COLOR, rect, 2)
            # Отображаем количество побед
            win_text = f"Победы: {wins}"
            win_surf = font.render(win_text, True, WHITE_COLOR)
            screen.blit(win_surf, (OFFSET_X, OFFSET_Y - 150))

        # Отображаем количество побед (дублируется, можно убрать одну)
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
