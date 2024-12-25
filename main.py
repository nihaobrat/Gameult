import tkinter as tk
import colorsys
import random
import subprocess
import sys
import os
from PIL import Image, ImageDraw, ImageTk

# Определяем директорию, в которой находится main.py
script_dir = os.path.dirname(os.path.abspath(__file__))

# ---------------------
# НАСТРОЙКА ОКНА TKINTER
# ---------------------
app = tk.Tk()
app.title("GAMEULT")
app.geometry("1920x1080")
app.configure(bg="#2c003e")
app.attributes("-fullscreen", True)  # Полноэкранный режим

# ---------------------
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ---------------------
selected_button_index = 0  # Для главных кнопок ("Играть" и "Выйти")
selected_game_index = 0    # Для списка игр
buttons = []
button_hue = 0             # Для анимации кнопок

# Список игр (удалена "TetrisULT")
game_list = [
    "AgarioULT",
    "SnakeULT",
    "HangmanULT",
    "TicTacToeULT",
    "PongULT",
    "MinesweeperULT",
]

# ---------------------
# АНИМАЦИЯ КНОПОК
# ---------------------
def animate_button_colors():
    global button_hue
    rgb = colorsys.hsv_to_rgb(button_hue, 0.5, 1)
    rgb = tuple(int(c * 255) for c in rgb)
    hex_color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    for button in buttons:
        button.config(bg=hex_color, activebackground=hex_color)
    button_hue += 0.01
    if button_hue > 1:
        button_hue = 0
    app.after(100, animate_button_colors)

# ---------------------
# АНИМАЦИИ НА ГЛАВНОМ ЭКРАНЕ
# ---------------------
# Canvas для анимаций (фон)
animation_canvas = tk.Canvas(app, width=1920, height=1080, bg="#2c003e", highlightthickness=0)
animation_canvas.pack(fill="both", expand=True)

# Ползающие змейки
class Snake:
    def __init__(self, canvas, length=15):
        self.canvas = canvas
        self.length = length
        self.segments = []
        self.direction = random.choice(["left", "right", "up", "down"])
        self.speed = 10  # Увеличенная скорость
        self.hue = random.random()  # Начальный оттенок
        self.create_snake()

    def create_snake(self):
        start_x = random.randint(100, 1820)
        start_y = random.randint(100, 980)
        for i in range(self.length):
            color = self.get_color()
            segment = self.canvas.create_rectangle(
                start_x - i*20, start_y,
                start_x - i*20 + 15, start_y + 15,
                fill=color, outline=""
            )
            self.segments.append(segment)

    def get_color(self):
        rgb = colorsys.hsv_to_rgb(self.hue, 1, 1)
        rgb = tuple(int(c * 255) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def update_color(self):
        self.hue += 0.005
        if self.hue > 1:
            self.hue = 0

    def move(self):
        self.update_color()
        head_coords = self.canvas.coords(self.segments[0])
        if self.direction == "left":
            dx, dy = -self.speed, 0
        elif self.direction == "right":
            dx, dy = self.speed, 0
        elif self.direction == "up":
            dx, dy = 0, -self.speed
        else:
            dx, dy = 0, self.speed

        # Проверка границ
        if head_coords[0] + dx < 0 or head_coords[2] + dx > 1920:
            self.direction = random.choice(["up", "down"])
        if head_coords[1] + dy < 0 or head_coords[3] + dy > 1080:
            self.direction = random.choice(["left", "right"])

        # Передвигаем все сегменты
        for i in range(len(self.segments)-1, 0, -1):
            coords = self.canvas.coords(self.segments[i-1])
            self.canvas.coords(
                self.segments[i],
                coords[0], coords[1],
                coords[0] + 15, coords[1] + 15
            )
        self.canvas.move(self.segments[0], dx, dy)

        # Обновляем цвет всех сегментов
        for segment in self.segments:
            self.canvas.itemconfig(segment, fill=self.get_color())

# Шарики Agario
class AgarioBall:
    def __init__(self, canvas):
        self.canvas = canvas
        self.radius = random.randint(10, 30)
        self.x = random.randint(self.radius, 1920 - self.radius)
        self.y = random.randint(self.radius, 1080 - self.radius)
        self.dx = random.choice([-5, -4, -3, 3, 4, 5])  # Увеличенная скорость
        self.dy = random.choice([-5, -4, -3, 3, 4, 5])
        self.hue = random.random()
        self.create_ball()

    def create_ball(self):
        color = self.get_color()
        self.ball = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=color, outline=""
        )

    def get_color(self):
        rgb = colorsys.hsv_to_rgb(self.hue, 1, 1)
        rgb = tuple(int(c * 255) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def update_color(self):
        self.hue += 0.003
        if self.hue > 1:
            self.hue = 0

    def move(self):
        self.update_color()
        self.canvas.move(self.ball, self.dx, self.dy)
        coords = self.canvas.coords(self.ball)
        if coords[0] < 0 or coords[2] > 1920:
            self.dx *= -1
        if coords[1] < 0 or coords[3] > 1080:
            self.dy *= -1

        # Обновляем цвет шара
        self.canvas.itemconfig(self.ball, fill=self.get_color())

# Генерирующиеся крестики-нолики
class TicTacToeSymbol:
    def __init__(self, canvas, symbol="X", color="#ffffff"):
        self.canvas = canvas
        self.symbol = symbol
        self.color = color
        self.size = 30
        self.x = random.randint(50, 1870)
        self.y = random.randint(50, 1030)
        self.create_symbol()

    def create_symbol(self):
        if self.symbol == "X":
            self.line1 = self.canvas.create_line(
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size,
                fill=self.color, width=3
            )
            self.line2 = self.canvas.create_line(
                self.x - self.size, self.y + self.size,
                self.x + self.size, self.y - self.size,
                fill=self.color, width=3
            )
        else:
            self.circle = self.canvas.create_oval(
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size,
                outline=self.color, width=3
            )

    def remove_symbol(self):
        if self.symbol == "X":
            self.canvas.delete(self.line1)
            self.canvas.delete(self.line2)
        else:
            self.canvas.delete(self.circle)

# Создание анимационных объектов (Только один раз)
num_snakes = 15  # Увеличено количество змей
num_agario_balls = 50  # Увеличено количество шариков Agario

snakes = [Snake(animation_canvas, length=15) for _ in range(num_snakes)]
agario_balls = [AgarioBall(animation_canvas) for _ in range(num_agario_balls)]
tic_tac_toe_symbols = []

def generate_tic_tac_toe_symbol():
    symbol = random.choice(["X", "O"])
    color = "#ffffff"
    ttt_symbol = TicTacToeSymbol(animation_canvas, symbol, color)
    tic_tac_toe_symbols.append(ttt_symbol)
    # Удаляем символ через 3 секунды
    app.after(3000, ttt_symbol.remove_symbol)
    app.after(3000, lambda: tic_tac_toe_symbols.remove(ttt_symbol))

def animate():
    # Передвижение змей
    for snake in snakes:
        snake.move()

    # Передвижение шариков Agario
    for ball in agario_balls:
        ball.move()

    # Генерация символов крестиков-ноликов
    if random.randint(1, 100) <= 2:  # 2% шанс генерации символа
        generate_tic_tac_toe_symbol()

    app.after(50, animate)  # Рекурсивный вызов через 50 мс

animate()  # Запуск анимации

# ---------------------
# ЗАГОЛОВОК
# ---------------------
# Создаём отдельный Frame для главного экрана
main_frame = tk.Frame(app, bg="#2c003e")
main_frame.place(relx=0.5, rely=0.5, anchor="center")

title_label = tk.Label(main_frame, text="GAMEULT", font=("Helvetica", 120, "bold"), fg="#00ff00", bg="#2c003e")
title_label.pack(pady=(0, 50))  # Отступ снизу для разделения с кнопками

# ---------------------
# РАМКА ДЛЯ КНОПОК "ИГРАТЬ" И "ВЫЙТИ" (вертикально)
# ---------------------
buttons_frame = tk.Frame(main_frame, bg="#2c003e")
buttons_frame.pack()

def highlight_selected_button():
    for i, button in enumerate(buttons):
        if i == selected_button_index:
            button.config(bg="#cce7cc", fg="black", font=("Helvetica", 24, "bold"))  # Увеличенный шрифт для выбранной кнопки
        else:
            button.config(bg="#e6e6e6", fg="black", font=("Helvetica", 20))

def navigate_buttons(event):
    global selected_button_index
    if event.keysym == "Up":
        selected_button_index = (selected_button_index - 1) % len(buttons)
    elif event.keysym == "Down":
        selected_button_index = (selected_button_index + 1) % len(buttons)
    highlight_selected_button()

def select_button(event):
    if selected_button_index == 0:
        show_game_list()
    elif selected_button_index == 1:
        exit_app()

# ---------------------
# КНОПКИ ГЛАВНОГО ЭКРАНА (вертикально)
# ---------------------
play_button = tk.Button(
    buttons_frame, 
    text="Играть", 
    command=lambda: show_game_list(),
    font=("Helvetica", 20, "bold"),
    fg="black", 
    bg="#e6e6e6",
    activebackground="#cccccc", 
    borderwidth=10,
    width=20,
    height=2
)
play_button.pack(pady=20)  # Отступы между кнопками

exit_button = tk.Button(
    buttons_frame, 
    text="Выйти", 
    command=lambda: exit_app(),
    font=("Helvetica", 20, "bold"), 
    fg="black", 
    bg="#e6e6e6",
    activebackground="#cccccc", 
    borderwidth=10,
    width=20,
    height=2
)
exit_button.pack(pady=20)

buttons.extend([play_button, exit_button])
highlight_selected_button()

# ---------------------
# GAME LIST ОКНО С ГОРИЗОНТАЛЬНЫМ СПИСКОМ ИГР
# ---------------------
# Создаём отдельный Frame для списка игр
game_list_frame = tk.Frame(app, bg="#2c003e")

# Canvas для списка игр
game_canvas = tk.Canvas(game_list_frame, width=1200, height=700, bg="#2c003e", highlightthickness=0)
game_canvas.pack(expand=True)

# Создаём Frame внутри game_canvas для отображения игр
game_frame = tk.Frame(game_canvas, bg="#2c003e")
game_frame.place(relx=0.5, rely=0.5, anchor="center")

# Кнопка "Назад"
back_button_game = tk.Button(
    game_frame, 
    text="Назад", 
    font=("Helvetica", 20, "bold"),
    fg="black", 
    bg="#e6e6e6", 
    activebackground="#cccccc",
    borderwidth=4,
    command=lambda: hide_game_list()
)
back_button_game.pack(side="bottom", pady=20)

# Кнопки для навигации по играм
navigation_frame = tk.Frame(game_frame, bg="#2c003e")
navigation_frame.pack(pady=20)

left_game_btn = tk.Button(
    navigation_frame, 
    text="", 
    font=("Helvetica", 15),
    fg="white", 
    bg="#4a148c",
    activebackground="#7b1fa2",
    borderwidth=2,
    relief="raised",
    bd=4,
    width=15,
    command=lambda: navigate_game(-1)
)
left_game_btn.pack(side="left", padx=50, pady=50)

center_game_btn = tk.Button(
    navigation_frame, 
    text="", 
    font=("Helvetica", 25, "bold"),
    fg="black",  # Черный цвет для лучшего контраста
    bg="#00ff00",  # Изменён на зелёный фон для центральной кнопки
    activebackground="#a5d6a7",  # Более темный оттенок при активном состоянии
    borderwidth=4,
    relief="sunken",  # Визуально выделена
    bd=4,
    width=20,
    command=lambda: select_current_game()
)
center_game_btn.pack(side="left", padx=50, pady=50)

right_game_btn = tk.Button(
    navigation_frame, 
    text="", 
    font=("Helvetica", 15),
    fg="white", 
    bg="#4a148c",
    activebackground="#7b1fa2",
    borderwidth=2,
    relief="raised",
    bd=4,
    width=15,
    command=lambda: navigate_game(1)
)
right_game_btn.pack(side="left", padx=50, pady=50)

def update_game_display():
    left_index = (selected_game_index - 1) % len(game_list)
    right_index = (selected_game_index + 1) % len(game_list)
    left_game_btn.config(text=game_list[left_index], bg="#4a148c")
    center_game_btn.config(text=game_list[selected_game_index], bg="#00ff00")  # Центральная кнопка теперь зелёная
    right_game_btn.config(text=game_list[right_index], bg="#4a148c")

def navigate_game(direction):
    global selected_game_index
    selected_game_index = (selected_game_index + direction) % len(game_list)
    update_game_display()
    highlight_selected_element()

def select_current_game():
    selected_game = game_list[selected_game_index]
    select_game(selected_game)

# ---------------------
# ФУНКЦИИ ЗАПУСКА ИГР
# ---------------------
def run_snake_game():
    try:
        subprocess.Popen([sys.executable, os.path.join(script_dir, "snakeult.py")])
    except Exception as e:
        print(f"Ошибка при запуске SnakeULT: {e}")

def run_agario_game():
    try:
        agario_process = subprocess.Popen([sys.executable, os.path.join(script_dir, "agarioult.py")])
        agario_process.wait()
        show_game_list()
    except Exception as e:
        print(f"Ошибка при запуске AgarioULT: {e}")

def run_hangman_game():
    try:
        hangman_process = subprocess.Popen([sys.executable, os.path.join(script_dir, "hangmanult.py")])
        hangman_process.wait()
        show_game_list()
    except Exception as e:
        print(f"Ошибка при запуске HangmanULT: {e}")

def run_tictactoe_game():
    try:
        tictactoe_process = subprocess.Popen([sys.executable, os.path.join(script_dir, "tictactoeult.py")])
        tictactoe_process.wait()
        show_game_list()
    except Exception as e:
        print(f"Ошибка при запуске TicTacToeULT: {e}")

def run_pong_game():
    try:
        pong_process = subprocess.Popen([sys.executable, os.path.join(script_dir, "pongult.py")])
        pong_process.wait()
        show_game_list()
    except Exception as e:
        print(f"Ошибка при запуске PongULT: {e}")

def run_minesweeper_game():
    try:
        mines_process = subprocess.Popen([sys.executable, os.path.join(script_dir, "minesweeperult.py")])
        mines_process.wait()
        show_game_list()
    except Exception as e:
        print(f"Ошибка при запуске MinesweeperULT: {e}")

def select_game(game_name):
    if game_name == "SnakeULT":
        run_snake_game()
    elif game_name == "AgarioULT":
        run_agario_game()
    elif game_name == "HangmanULT":
        run_hangman_game()
    elif game_name == "TicTacToeULT":
        run_tictactoe_game()
    elif game_name == "PongULT":
        run_pong_game()
    elif game_name == "MinesweeperULT":
        run_minesweeper_game()
    elif game_name == "Назад":
        hide_game_list()

# ---------------------
# ПЕРЕКЛЮЧЕНИЕ МЕЖДУ ГЛАВНЫМ ЭКРАНОМ И СПИСКОМ ИГР
# ---------------------
def show_game_list():
    main_frame.place_forget()  # Скрываем главный экран
    game_list_frame.place(relx=0.5, rely=0.5, anchor="center")  # Показываем список игр
    global selected_game_index
    selected_game_index = 0
    update_game_display()
    highlight_selected_element()
    app.bind("<Left>", navigate_game_left)
    app.bind("<Right>", navigate_game_right)
    app.bind("<Down>", navigate_to_back)
    app.bind("<Return>", select_game_with_keys)
    # Начинаем анимацию прокрутки (пока без реализации)
    animate_scroll()

def hide_game_list():
    game_list_frame.place_forget()  # Скрываем список игр
    main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Показываем главный экран
    highlight_selected_button()
    app.unbind("<Left>")
    app.unbind("<Right>")
    app.unbind("<Down>")
    app.unbind("<Return>")
    app.bind("<Up>", navigate_buttons)
    app.bind("<Down>", navigate_buttons)

def exit_app():
    app.quit()

# ---------------------
# НАВИГАЦИЯ И ВЫБОР ИГР
# ---------------------
def highlight_selected_element():
    # Подсвечиваем центральную кнопку игры зелёным цветом
    center_game_btn.config(bg="#00ff00", fg="white")  # Зелёный фон, белый текст
    left_game_btn.config(bg="#4a148c", fg="white")
    right_game_btn.config(bg="#4a148c", fg="white")
    center_game_btn.config(relief="sunken")
    left_game_btn.config(relief="raised")
    right_game_btn.config(relief="raised")

def navigate_game_left(event):
    navigate_game(-1)

def navigate_game_right(event):
    navigate_game(1)

def navigate_to_back(event):
    if event.keysym == "Down":
        # Фокусируемся на кнопке "Назад"
        back_button_game.focus_set()
        back_button_game.config(bg="#ff0000", fg="white")  # Красный фон, белый текст

def select_game_with_keys(event):
    if app.focus_get() == back_button_game:
        select_game("Назад")
    else:
        select_game(game_list[selected_game_index])

# ---------------------
# ПЛАВНОЕ ПРОКРУЧИВАНИЕ СПИСКА ИГР
# ---------------------
def animate_scroll():
    # Плавное прокручивание реализовано путем изменения позиции фрейма
    # Для упрощения оставим базовую реализацию без анимации
    pass  # Место для будущей доработки

# ---------------------
# START MAINLOOP
# ---------------------
# Начальные привязки клавиш для главного экрана
app.bind("<Up>", navigate_buttons)
app.bind("<Down>", navigate_buttons)
app.bind("<Return>", select_button)

# Запуск анимации цветов кнопок
animate_button_colors()

app.mainloop()
