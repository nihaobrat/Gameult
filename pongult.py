"""
Файл: pongult.py
Описание:
    - Игра PongULT (аэрохоккей) в полноэкранном режиме.
    - "Поле" 1280x720 рисуется по центру экрана, чтобы при больших мониторах само поле было строго по центру.
    - Главное меню (Начать играть, Выйти).
    - Меню выбора сложности (Медленный, Обычный, Сложный) + кнопка "Назад" (возврат в главное меню).
    - Один игрок: левый = бот (AI), правый = стрелки.
    - Меню паузы (ESC) с пунктами (Продолжить / В главное меню).
    - Сохранение лучшего счёта ("pongult_score.txt"), таймер, визуальные эффекты при голах.
"""

import pygame
import sys
import os
import random
import math
import colorsys

# ===== ПАРАМЕТРЫ "ИГРОВОГО ПОЛЯ" =====
GAME_WIDTH  = 1280
GAME_HEIGHT = 720

# ===== ИНИЦИАЛИЗАЦИЯ PYGAME =====
pygame.init()
# Полноэкранный режим
info = pygame.display.Info()
monitor_w, monitor_h = info.current_w, info.current_h

screen = pygame.display.set_mode((monitor_w, monitor_h), pygame.FULLSCREEN)
pygame.display.set_caption("PongULT")
clock = pygame.time.Clock()

# ===== РАССЧИТЫВАЕМ ОФФСЕТ ДЛЯ ОТРИСОВКИ ПОЛЯ ПО ЦЕНТРУ =====
offset_x = (monitor_w - GAME_WIDTH) // 2
offset_y = (monitor_h - GAME_HEIGHT) // 2

# ===== ЦВЕТА =====
BACKGROUND_COLOR = (30, 30, 30)
WHITE_COLOR      = (255, 255, 255)
FLASH_COLOR      = (255, 0, 0)
GREEN_COLOR      = (0, 255, 0)
PAUSE_OVERLAY    = (0, 0, 0, 180)

# ===== ПАРАМЕТРЫ ИГРЫ =====
PADDLE_WIDTH   = 20
PADDLE_HEIGHT  = 100
PADDLE_SPEED   = 10
BALL_SIZE      = 20
WIN_SCORE      = 5

GOAL_HEIGHT    = 150
GOAL_MIN_Y     = (GAME_HEIGHT - GOAL_HEIGHT)//2
GOAL_MAX_Y     = (GAME_HEIGHT + GOAL_HEIGHT)//2

# ===== ШРИФТЫ =====
font_large = pygame.font.SysFont("Helvetica", 60, bold=True)
font_medium = pygame.font.SysFont("Helvetica", 60, bold=True)  # Добавлен font_medium
font_small = pygame.font.SysFont("Helvetica", 30, bold=True)
font_pause = pygame.font.SysFont("Helvetica", 100, bold=True)

# ===== ЗАГРУЗКА/СОХРАНЕНИЕ СЧЁТА =====
def load_high_score():
    if os.path.exists("pongult_score.txt"):
        try:
            with open("pongult_score.txt","r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(score):
    with open("pongult_score.txt","w") as f:
        f.write(str(score))

# ===== АНИМАЦИЯ ФОНА =====
def animate_background():
    hue = (pygame.time.get_ticks()*0.0005)%1
    r,g,b = colorsys.hsv_to_rgb(hue,0.5,0.5)
    return (int(r*255), int(g*255), int(b*255))

def animate_text_blink(text, font, color, center, position, phase_speed=0.005):
    phase = math.sin(pygame.time.get_ticks()*phase_speed)
    alpha = abs(int(phase * 255))
    srf = font.render(text, True, color)
    blink_srf = pygame.Surface(srf.get_size(), pygame.SRCALPHA)
    blink_srf.blit(srf,(0,0))
    blink_srf.set_alpha(alpha)
    if center:
        rect = blink_srf.get_rect(center=position)
    else:
        rect = blink_srf.get_rect(topleft=position)
    screen.blit(blink_srf, rect)

# ===== МЕНЮ ПАУЗЫ (СТРЕЛКИ) =====
def pause_menu():
    items=["Продолжить","В главное меню"]
    idx=0
    in_pause=True
    while in_pause:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    idx=(idx-1)%len(items)
                elif event.key==pygame.K_DOWN:
                    idx=(idx+1)%len(items)
                elif event.key==pygame.K_RETURN:
                    if idx==0:
                        return "continue"
                    else:
                        return "menu"

        # Отрисовка
        overlay=pygame.Surface((monitor_w, monitor_h),pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY)
        screen.blit(overlay,(0,0))

        animate_text_blink("PAUSED", font_pause, WHITE_COLOR, True, (monitor_w//2, monitor_h//3))
        for i,item in enumerate(items):
            color=WHITE_COLOR
            if i==idx:
                color=FLASH_COLOR
            srf=font_medium.render(item,True,color)  # Используем font_medium
            r=srf.get_rect(center=(monitor_w//2, monitor_h//2 + i*50))
            screen.blit(srf,r)

        pygame.display.flip()
        clock.tick(60)

# ===== МЕНЮ ВЫБОРА СЛОЖНОСТИ (СТРЕЛКИ, + "НАЗАД") =====
def select_difficulty():
    diffs=[
        ("Медленный",4,4),
        ("Обычный",6,6),
        ("Сложный",9,9),
        ("Назад",0,0)  # При "Назад" вернём None
    ]
    idx=0
    while True:
        bg=animate_background()
        screen.fill(bg)
        title_srf = font_large.render("Сложность:",True,WHITE_COLOR)
        title_rect=title_srf.get_rect(center=(monitor_w//2, monitor_h//3))
        screen.blit(title_srf,title_rect)

        for i,(name,ball_s,ai_s) in enumerate(diffs):
            color=WHITE_COLOR
            if i==idx:
                color=FLASH_COLOR
            srf=font_medium.render(name,True,color)  # Используем font_medium
            r=srf.get_rect(center=(monitor_w//2, monitor_h//2 + i*50))
            screen.blit(srf,r)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    idx=(idx-1)%len(diffs)
                elif event.key==pygame.K_DOWN:
                    idx=(idx+1)%len(diffs)
                elif event.key==pygame.K_RETURN:
                    name, ball_s, ai_s = diffs[idx]
                    if name=="Назад":
                        return None
                    else:
                        return (name, ball_s, ai_s)

# ===== ГЛАВНОЕ МЕНЮ (НАЧАТЬ / ВЫЙТИ) =====
def main_menu():
    items=["Начать играть","Выйти"]
    idx=0
    while True:
        bg=animate_background()
        screen.fill(bg)

        t_srf=font_large.render("PongULT",True,WHITE_COLOR)
        t_rect=t_srf.get_rect(center=(monitor_w//2, monitor_h//3))
        screen.blit(t_srf,t_rect)

        for i, it in enumerate(items):
            color=WHITE_COLOR
            if i==idx:
                color=FLASH_COLOR
            srf=font_medium.render(it,True,color)  # Используем font_medium
            rr=srf.get_rect(center=(monitor_w//2, monitor_h//2 + i*50))
            screen.blit(srf,rr)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    idx=(idx-1)%len(items)
                elif event.key==pygame.K_DOWN:
                    idx=(idx+1)%len(items)
                elif event.key==pygame.K_RETURN:
                    if idx==0:
                        return "start"
                    else:
                        pygame.quit()
                        sys.exit()

# ===== ОТРИСОВКА СЧЁТА / GAME OVER =====
def draw_score(score_left, score_right, high_score):
    txt = f"{score_left} : {score_right}"
    srf = font_large.render(txt,True,WHITE_COLOR)
    screen.blit(srf,(offset_x+GAME_WIDTH//2 - srf.get_width()//2, offset_y+20))

    best_txt = f"Лучший счёт: {high_score}"
    best_srf = font_small.render(best_txt,True,WHITE_COLOR)
    screen.blit(best_srf,(offset_x+GAME_WIDTH - best_srf.get_width()-50, offset_y+20))

def draw_game_over(winner, high_score, score_left, score_right, hit_left, hit_right):
    if winner:
        msg=f"Победил {'Левый' if winner=='left' else 'Правый'} игрок!"
        animate_text_blink(msg, font_large, WHITE_COLOR, True,(monitor_w//2, monitor_h//2 -80))
    else:
        msg="Ничья!"
        srf=font_large.render(msg,True,WHITE_COLOR)
        rect=srf.get_rect(center=(monitor_w//2, monitor_h//2-80))
        screen.blit(srf,rect)

    lines=["Нажмите Enter для перезапуска","Нажмите ESC для выхода в меню"]
    for i,ln in enumerate(lines):
        animate_text_blink(ln, font_small, WHITE_COLOR, True,(monitor_w//2, monitor_h//2 + i*40))

    if winner:
        high_score = max(high_score, score_left if winner=="left" else score_right)
    return high_score

# ===== РИСУЕМ РАМКУ + ОТВЕРСТИЯ, С УЧЁТОМ offset_x/y =====
def draw_frame_and_goals():
    thickness=10
    # Сверху
    pygame.draw.line(screen,WHITE_COLOR,(offset_x,offset_y),
                     (offset_x+GAME_WIDTH, offset_y), thickness)
    # Снизу
    pygame.draw.line(screen,WHITE_COLOR,(offset_x, offset_y+GAME_HEIGHT),
                     (offset_x+GAME_WIDTH, offset_y+GAME_HEIGHT), thickness)

    # Лево
    pygame.draw.line(screen,WHITE_COLOR,(offset_x, offset_y),
                     (offset_x, offset_y+GOAL_MIN_Y), thickness)
    pygame.draw.line(screen,WHITE_COLOR,(offset_x, offset_y+GOAL_MAX_Y),
                     (offset_x, offset_y+GAME_HEIGHT), thickness)

    # Право
    pygame.draw.line(screen,WHITE_COLOR,(offset_x+GAME_WIDTH, offset_y),
                     (offset_x+GAME_WIDTH, offset_y+GOAL_MIN_Y), thickness)
    pygame.draw.line(screen,WHITE_COLOR,(offset_x+GAME_WIDTH, offset_y+GOAL_MAX_Y),
                     (offset_x+GAME_WIDTH, offset_y+GAME_HEIGHT), thickness)

# ===== КЛАСС РАКЕТКИ =====
class Paddle:
    def __init__(self,x,y):
        self.x=float(x)
        self.y=float(y)
        self.width=PADDLE_WIDTH
        self.height=PADDLE_HEIGHT
        self.speed=float(PADDLE_SPEED)
        self.flash_timer=0
        self.rect=pygame.Rect(0,0,self.width,self.height)
    def move_up(self):
        self.y-=self.speed
        if self.y<0: self.y=0
    def move_down(self):
        self.y+=self.speed
        if self.y+self.height>GAME_HEIGHT:
            self.y=GAME_HEIGHT-self.height
    def draw(self):
        color=WHITE_COLOR
        if self.flash_timer>0:
            color=FLASH_COLOR
            self.flash_timer-=1
        self.rect.x=int(offset_x + self.x)
        self.rect.y=int(offset_y + self.y)
        pygame.draw.rect(screen, color, self.rect)
    def flash_hit(self):
        self.flash_timer=15

# ===== КЛАСС МЯЧА =====
class Ball:
    def __init__(self):
        self.size=BALL_SIZE
        self.x=float(GAME_WIDTH//2)
        self.y=float(GAME_HEIGHT//2)
        self.dx=0
        self.dy=0
        self.rect=pygame.Rect(0,0,self.size,self.size)
    def reset(self,speed=6):
        self.x=GAME_WIDTH/2
        self.y=GAME_HEIGHT/2
        self.dx = speed if random.choice([True,False]) else -speed
        self.dy = speed if random.choice([True,False]) else -speed
    def update(self,left_paddle,right_paddle, ball_speed):
        self.x+=self.dx
        self.y+=self.dy

        # Верх/низ
        if self.y<0:
            self.y=0
            self.dy=-self.dy
        elif self.y+self.size>GAME_HEIGHT:
            self.y=GAME_HEIGHT-self.size
            self.dy=-self.dy

        # rect
        self.rect.x=int(offset_x + self.x)
        self.rect.y=int(offset_y + self.y)
        self.rect.width=self.size
        self.rect.height=self.size

        # paddle rect
        lrect=pygame.Rect(offset_x + left_paddle.x,
                          offset_y + left_paddle.y,
                          left_paddle.width, left_paddle.height)
        rrect=pygame.Rect(offset_x + right_paddle.x,
                          offset_y + right_paddle.y,
                          right_paddle.width,right_paddle.height)

        if self.rect.colliderect(lrect):
            if self.dx<0:
                self.dx=-self.dx
                left_paddle.flash_hit()
        elif self.rect.colliderect(rrect):
            if self.dx>0:
                self.dx=-self.dx
                right_paddle.flash_hit()

        # Левый край
        if self.x<0:
            center_y=self.y+self.size/2
            if GOAL_MIN_Y<=center_y<=GOAL_MAX_Y:
                return "goal_left"
            else:
                self.x=0
                self.dx=-self.dx
        # Правый край
        if self.x+self.size>GAME_WIDTH:
            center_y=self.y+self.size/2
            if GOAL_MIN_Y<=center_y<=GOAL_MAX_Y:
                return "goal_right"
            else:
                self.x=GAME_WIDTH-self.size
                self.dx=-self.dx
        return None
    def draw(self):
        self.rect.x=int(offset_x + self.x)
        self.rect.y=int(offset_y + self.y)
        pygame.draw.ellipse(screen, GREEN_COLOR, self.rect)

# ===== ФУНКЦИЯ ЗАПУСКА ИГРЫ =====
def run_game(ball_speed, ai_speed):
    left_paddle = Paddle(50, GAME_HEIGHT//2 - PADDLE_HEIGHT//2)
    right_paddle= Paddle(GAME_WIDTH-50-PADDLE_WIDTH, GAME_HEIGHT//2 - PADDLE_HEIGHT//2)
    ball=Ball()
    ball.reset(ball_speed)

    score_left=0
    score_right=0
    high_score=load_high_score()

    game_over=False
    winner=None
    hit_left=False
    hit_right=False

    start_time=pygame.time.get_ticks()

    # AI
    def left_ai():
        # Тянется к y мяча
        target = ball.y + ball.size/2
        # Двигаемся со speed=ai_speed
        if left_paddle.y + left_paddle.height/2 < target -10:
            left_paddle.y+=min(ai_speed, abs(left_paddle.y+left_paddle.height/2 - target))
        elif left_paddle.y + left_paddle.height/2 > target +10:
            left_paddle.y-=min(ai_speed, abs(left_paddle.y+left_paddle.height/2 - target))
        if left_paddle.y<0:
            left_paddle.y=0
        elif left_paddle.y+left_paddle.height>GAME_HEIGHT:
            left_paddle.y=GAME_HEIGHT-left_paddle.height

    paused=False
    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if not game_over:
                        # Меню паузы
                        pm_res = pause_menu()  # "continue" or "menu"
                        if pm_res=="continue":
                            pass
                        else:
                            # "menu"
                            running=False
                    else:
                        # game_over => ESC => выход в главное меню
                        running=False
                elif event.key==pygame.K_RETURN and game_over:
                    # Перезапуск
                    score_left=0
                    score_right=0
                    ball.reset(ball_speed)
                    game_over=False
                    winner=None
                    hit_left=False
                    hit_right=False
                    start_time=pygame.time.get_ticks()

        if not game_over:
            # Левый = AI
            left_ai()
            # Правый = стрелки
            keys=pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                right_paddle.move_up()
            if keys[pygame.K_DOWN]:
                right_paddle.move_down()

            # Мяч
            result=ball.update(left_paddle,right_paddle, ball_speed)
            if result=="goal_left":
                score_right+=1
                ball.reset(ball_speed)
                hit_left=True
                start_time=pygame.time.get_ticks()
            elif result=="goal_right":
                score_left+=1
                ball.reset(ball_speed)
                hit_right=True
                start_time=pygame.time.get_ticks()

            if score_left>=WIN_SCORE:
                game_over=True
                winner="left"
            elif score_right>=WIN_SCORE:
                game_over=True
                winner="right"

        # Отрисовка
        bg=animate_background()
        screen.fill(bg)

        draw_frame_and_goals()

        if game_over:
            high_score=draw_game_over(winner, high_score, score_left, score_right, hit_left, hit_right)
        else:
            left_paddle.draw()
            right_paddle.draw()
            ball.draw()
            draw_score(score_left, score_right, high_score)

            if hit_left:
                # Вспышка слева
                pygame.draw.rect(screen,FLASH_COLOR,(offset_x, offset_y, 20, GAME_HEIGHT))
                hit_left=False
            if hit_right:
                # Вспышка справа
                pygame.draw.rect(screen,FLASH_COLOR,(offset_x+GAME_WIDTH-20, offset_y, 20, GAME_HEIGHT))
                hit_right=False

            # Таймер
            elapsed=(pygame.time.get_ticks()-start_time)//1000
            srf=font_small.render(f"Время: {elapsed} сек",True,WHITE_COLOR)
            screen.blit(srf,(offset_x+GAME_WIDTH//2 - srf.get_width()//2, offset_y + GAME_HEIGHT-40))

        pygame.display.flip()
        clock.tick(60)

    # Сохранить счёт
    save_high_score(high_score)

# ===== MAIN =====
def main():
    while True:
        # Главное меню
        menu_res = main_menu()  # "start" / sys.exit()
        if menu_res!="start":
            # вышли
            pygame.quit()
            sys.exit()

        # Если "Начать играть"
        diff_res = None
        while diff_res is None:
            diff_res = select_difficulty()  # либо вернётся (name, speed, aispeed), либо None (Назад)
            if diff_res is None:
                # Нажали "Назад" => вернуться в главное меню
                break
        if diff_res is None:
            # вернулись => снова while True => главное меню
            continue
        # Иначе у нас (diff_name, ball_speed, ai_speed)
        diff_name, ball_speed, ai_speed = diff_res

        # Запускаем игру
        run_game(ball_speed, ai_speed)
        # По выходу из run_game() вернёмся сюда => заново в главный цикл (меню)        

if __name__=="__main__":
    main()
