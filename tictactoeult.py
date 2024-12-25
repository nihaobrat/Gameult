"""
TicTacToeULT
- Главное меню (Начать, Выйти)
- Меню выбора режима (робот, 2 игрока, назад)
- Поле 3x3 (CELL_SIZE=150), в полноэкранном режиме, 
  но само поле 450x450, расположенное по центру экрана.
- Сохранение счетов X и O в "tictactoeult_score.txt"
- Пауза (ESC) => (Продолжить / В меню выбора режима)
- Game Over => (ENTER - заново, ESC - в меню выбора режима)
- Робот с "задержкой" и анимацией (плавный рост символа).
- Если робот ходит первым, он сразу начинает анимацию.
"""

import pygame
import sys
import os
import math
import random
import time
import colorsys

# ================= PYGAME INIT =================
os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()
info = pygame.display.Info()
monitor_w, monitor_h = info.current_w, info.current_h
screen = pygame.display.set_mode((monitor_w, monitor_h), pygame.FULLSCREEN)
pygame.display.set_caption("TicTacToeULT")
clock = pygame.time.Clock()

# Параметры "игрового поля"
GAME_WIDTH  = 450  # 3 * 150
GAME_HEIGHT = 450
offset_x = (monitor_w - GAME_WIDTH)//2
offset_y = (monitor_h - GAME_HEIGHT)//2

# ================= COLORS =================
GRID_COLOR    = (200, 200, 200)
TEXT_COLOR    = (255, 255, 255)
X_COLOR       = (255, 50, 50)
O_COLOR       = (50, 200, 255)
PAUSE_OVERLAY = (0, 0, 0, 180)

# ================= GAME CONSTANTS =================
GRID_SIZE  = 3
CELL_SIZE  = 150
LINE_WIDTH = 10

font_large   = pygame.font.SysFont("Helvetica", 80,  bold=True)
font_small   = pygame.font.SysFont("Helvetica", 40,  bold=True)
font_pause   = pygame.font.SysFont("Helvetica", 100, bold=True)
font_medium  = pygame.font.SysFont("Helvetica", 60,  bold=True)

# Счёт X/O
def load_scores():
    if os.path.exists("tictactoeult_score.txt"):
        try:
            with open("tictactoeult_score.txt","r",encoding="utf-8") as f:
                xwins, owins = map(int,f.read().strip().split(";"))
                return xwins, owins
        except:
            return 0,0
    return 0,0

def save_scores(x, o):
    with open("tictactoeult_score.txt","w",encoding="utf-8") as f:
        f.write(f"{x};{o}")

x_wins, o_wins = load_scores()

# ====== BACKGROUND ANIMATION ======
animation_phase=0
def animate_background_slowdark():
    """Медленный, тёмный градиент HSV->RGB."""
    global animation_phase
    animation_phase += 0.2
    hue = (animation_phase%360)/360
    sat = 0.3
    val = 0.4
    r,g,b = colorsys.hsv_to_rgb(hue,sat,val)
    return (int(r*255), int(g*255), int(b*255))

# ====== MENU: MAIN (Начать, Выйти) ======
def main_menu():
    items=["Начать игру","Выйти"]
    idx=0
    while True:
        bg=animate_background_slowdark()
        screen.fill(bg)

        title_srf = font_pause.render("TicTacToeULT",True,(255,255,255))
        title_rect=title_srf.get_rect(center=(monitor_w//2, monitor_h//4))
        screen.blit(title_srf,title_rect)

        for i,text in enumerate(items):
            col=(255,255,255)
            if i==idx:
                col=(255,0,0)
            srf=font_medium.render(text,True,col)
            rr=srf.get_rect(center=(monitor_w//2, monitor_h//2 + i*80))
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

# ====== MENU: Выбор режима (робот, два игрока, назад) ======
def mode_menu():
    items=["Игра с роботом","Игра на 2 игроков","Назад"]
    idx=0
    while True:
        bg=animate_background_slowdark()
        screen.fill(bg)

        t_srf=font_medium.render("Выберите режим:",True,(255,255,255))
        t_rect=t_srf.get_rect(center=(monitor_w//2,monitor_h//4))
        screen.blit(t_srf,t_rect)

        for i,text in enumerate(items):
            col=(255,255,255)
            if i==idx:
                col=(255,0,0)
            srf=font_small.render(text,True,col)
            rr=srf.get_rect(center=(monitor_w//2, monitor_h//2 + i*60))
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
                        return "robot"
                    elif idx==1:
                        return "two"
                    else:
                        return None

# ====== MENU: Пауза (Продолжить / В меню выбора режима) ======
def pause_menu():
    items=["Продолжить","В меню выбора режима"]
    idx=0
    while True:
        overlay=pygame.Surface((monitor_w,monitor_h),pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY)
        screen.blit(overlay,(0,0))

        t_srf=font_pause.render("PAUSED",True,(255,255,255))
        t_rect=t_srf.get_rect(center=(monitor_w//2, monitor_h//4))
        screen.blit(t_srf,t_rect)

        for i,it in enumerate(items):
            col=(255,255,255)
            if i==idx:
                col=(255,0,0)
            srf=font_small.render(it,True,col)
            rr=srf.get_rect(center=(monitor_w//2, monitor_h//2 + i*60))
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
                        return "continue"
                    else:
                        return "menu"

# ====== ВВОД ИМЕНИ ======
def input_name(prompt_text):
    name=""
    done=False
    while not done:
        bg=animate_background_slowdark()
        screen.fill(bg)

        prompt_srf=font_small.render(prompt_text,True,(255,255,255))
        prompt_rect=prompt_srf.get_rect(center=(monitor_w//2, monitor_h//3))
        screen.blit(prompt_srf,prompt_rect)

        name_srf=font_small.render(name+"|",True,(255,255,255))
        name_rect=name_srf.get_rect(center=(monitor_w//2,monitor_h//2))
        screen.blit(name_srf,name_rect)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN:
                    done=True
                elif event.key==pygame.K_BACKSPACE:
                    name=name[:-1]
                elif event.key==pygame.K_ESCAPE:
                    return ""
                else:
                    name+=event.unicode
    return name.strip()

# ============ КЛАСС ИГРЫ ============
class TicTacToeGame:
    def __init__(self, names=("X","O"), is_robot=False):
        """
        names: [nameX, nameO]
        is_robot: bool, if True => nameO is robot
        """
        self.names = list(names)
        self.symbols = ["X","O"]
        self.current_index=0
        self.is_robot=is_robot
        self.board=[["" for _ in range(3)] for _ in range(3)]
        self.game_over=False
        self.winner=None

        # For robot animation
        self.robot_anim=False
        self.robot_timer=0.0
        self.robot_symbol_size=0.0
        self.robot_target_rc=None

    def random_first(self):
        """случайно выбираем, кто ходит первым"""
        if random.choice([True,False]):
            self.current_index=1
            if self.is_robot and self.current_index==1:
                self.start_robot_move()

    def handle_click(self, pos):
        if self.game_over: return
        if self.is_robot and self.current_index==1:
            # robot's turn
            return
        x,y=pos
        if not(offset_x<=x<offset_x+3*CELL_SIZE and offset_y<=y<offset_y+3*CELL_SIZE):
            return
        row=(y-offset_y)//CELL_SIZE
        col=(x-offset_x)//CELL_SIZE
        if self.board[row][col]=="":
            sym=self.symbols[self.current_index]
            self.board[row][col]=sym
            if self.check_win(sym):
                self.game_over=True
                self.winner=self.current_index
            elif self.is_draw():
                self.game_over=True
                self.winner=None
            else:
                self.current_index=(self.current_index+1)%2
                if self.is_robot and self.current_index==1:
                    self.start_robot_move()

    def check_win(self, sym):
        # row
        for r in range(3):
            if all(self.board[r][c]==sym for c in range(3)):
                return True
        # col
        for c in range(3):
            if all(self.board[r][c]==sym for r in range(3)):
                return True
        # diag
        if all(self.board[i][i]==sym for i in range(3)):
            return True
        if all(self.board[i][2-i]==sym for i in range(3)):
            return True
        return False

    def is_draw(self):
        for r in range(3):
            for c in range(3):
                if self.board[r][c]=="":
                    return False
        return True

    def start_robot_move(self):
        """Запускаем таймер "думает 0.5с", а затем анимируем появление символа (0..1)."""
        self.robot_anim=True
        self.robot_timer=time.time()+0.5
        self.robot_symbol_size=0.0
        empties=[(r,c) for r in range(3) for c in range(3) if self.board[r][c]==""]
        if not empties:
            return
        self.robot_target_rc=random.choice(empties)

    def update_robot(self):
        """Нужно в game loop вызывать постоянно."""
        if self.game_over: return
        if not(self.is_robot and self.current_index==1):
            return
        if not self.robot_anim:
            return

        now=time.time()
        if now<self.robot_timer:
            # robot thinking
            return
        # else start "symbol_size" anim
        if self.robot_symbol_size<1.0:
            self.robot_symbol_size+=0.04
            if self.robot_symbol_size>=1.0:
                # символ появляется
                r,c=self.robot_target_rc
                sym="O"
                self.board[r][c]=sym
                self.robot_anim=False
                self.robot_target_rc=None
                if self.check_win(sym):
                    self.game_over=True
                    self.winner=1
                elif self.is_draw():
                    self.game_over=True
                    self.winner=None
                else:
                    self.current_index=0

    def draw(self):
        bg=animate_background_slowdark()
        screen.fill(bg)

        # draw lines
        for i in range(1,3):
            # hor
            pygame.draw.line(screen, GRID_COLOR,
                             (offset_x, offset_y + i*CELL_SIZE),
                             (offset_x + 3*CELL_SIZE, offset_y + i*CELL_SIZE),
                             LINE_WIDTH)
            # ver
            pygame.draw.line(screen, GRID_COLOR,
                             (offset_x + i*CELL_SIZE, offset_y),
                             (offset_x + i*CELL_SIZE, offset_y + 3*CELL_SIZE),
                             LINE_WIDTH)

        # draw X/O
        for r in range(3):
            for c in range(3):
                sym=self.board[r][c]
                if sym=="X":
                    color=X_COLOR
                    srf=font_large.render("X",True,color)
                    rr=srf.get_rect(center=(offset_x + c*CELL_SIZE + CELL_SIZE//2,
                                            offset_y + r*CELL_SIZE + CELL_SIZE//2))
                    screen.blit(srf,rr)
                elif sym=="O":
                    color=O_COLOR
                    srf=font_large.render("O",True,color)
                    rr=srf.get_rect(center=(offset_x + c*CELL_SIZE + CELL_SIZE//2,
                                            offset_y + r*CELL_SIZE + CELL_SIZE//2))
                    screen.blit(srf,rr)

        # если робот анимирует ход
        if self.robot_anim and self.robot_target_rc:
            r,c=self.robot_target_rc
            scale=self.robot_symbol_size
            color=O_COLOR
            srf=font_large.render("O",True,color)
            w,h=srf.get_size()
            nw=int(w*scale)
            nh=int(h*scale)
            if nw>0 and nh>0:
                srf2=pygame.transform.smoothscale(srf,(nw,nh))
                rr=srf2.get_rect(center=(offset_x + c*CELL_SIZE + CELL_SIZE//2,
                                         offset_y + r*CELL_SIZE + CELL_SIZE//2))
                screen.blit(srf2,rr)

        # чей ход
        if not self.game_over:
            text=f"Ход: {self.names[self.current_index]}"
            srf=font_small.render(text,True,(255,255,255))
            rr=srf.get_rect(center=(monitor_w//2, offset_y-60))
            screen.blit(srf,rr)

        # если game over
        if self.game_over:
            bottom_y=offset_y+3*CELL_SIZE+30
            if self.winner is None:
                msg="Ничья!"
            else:
                msg=f"Победил {self.names[self.winner]}!"
            srf=font_small.render(msg,True,(255,255,255))
            rr=srf.get_rect(center=(monitor_w//2,bottom_y+30))
            screen.blit(srf,rr)

            hint=font_small.render("Enter - заново, ESC - меню",True,(255,255,255))
            hint_rect=hint.get_rect(center=(monitor_w//2, bottom_y+80))
            screen.blit(hint,hint_rect)

# ====== RUN ONE MATCH =====
def run_tictactoe(names, is_robot=False):
    global x_wins, o_wins
    game = TicTacToeGame(names,is_robot)
    # random who first
    if is_robot:
        game.random_first()

    while True:
        game.update_robot()

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                game.handle_click(pygame.mouse.get_pos())
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    # pause
                    pm_res=pause_menu()  # "continue"/"menu"
                    if pm_res=="continue":
                        pass
                    else:
                        # "menu"
                        return
                elif event.key==pygame.K_RETURN and game.game_over:
                    # restart
                    if game.winner is not None:
                        # increment
                        w_ind=game.winner
                        sym=game.symbols[w_ind]
                        if sym=="X":
                            x_wins+=1
                        else:
                            o_wins+=1
                        save_scores(x_wins,o_wins)
                    # new
                    game = TicTacToeGame(names,is_robot)
                    if is_robot:
                        game.random_first()

        game.draw()
        pygame.display.flip()
        clock.tick(60)

# ===== MAIN =====
def main():
    global x_wins, o_wins
    while True:
        mm=main_menu()  # "start"/exit
        if mm!="start":
            pygame.quit()
            sys.exit()

        # меню выбора режима
        mode=mode_menu()  # "robot"/"two"/None
        if mode is None:
            continue
        if mode=="robot":
            names=["Вы","Робот"]
            run_tictactoe(names,True)
        else:
            # "two"
            p1=input_name("Имя первого игрока (X)?")
            if not p1:
                continue
            p2=input_name("Имя второго игрока (O)?")
            if not p2:
                continue
            names=[p1,p2]
            run_tictactoe(names,False)

if __name__=="__main__":
    main()
