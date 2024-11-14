import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import colorsys
import random
import subprocess
import os
import subprocess 

# Создаем основное окно
app = tk.Tk()
app.title("Добро пожаловать в Игровое Приложение")
app.geometry("1920x1080")
app.configure(bg="#2c003e")
app.attributes("-fullscreen", True)  # Полноэкранный режим

# Переменные для отслеживания цвета и текущего выделенного элемента
button_hue = 0
selected_button_index = 0
buttons = []

# Параметры для анимации
balls = []
snakes = []
num_balls = 55
num_snakes = 15
ball_speed = 6
snake_speed = 4
ball_animation_active = True

# Canvas для анимации шаров и змей
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
background_canvas = tk.Canvas(app, width=screen_width, height=screen_height, bg="#2c003e", highlightthickness=0)
background_canvas.place(x=0, y=0)

# Функция для плавного изменения цвета кнопок
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

# Функция для анимации рамки вокруг заголовка с надписью GAMEULT
border_hue = 0
def animate_border():
    global border_hue
    rgb = colorsys.hsv_to_rgb(border_hue, 0.7, 0.9)  # Настраиваем насыщенность и яркость
    hex_color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
    border_canvas.itemconfig(border_rect, outline=hex_color)
    border_hue += 0.01
    if border_hue > 1:
        border_hue = 0
    app.after(50, animate_border)

# Заголовок с анимированной прямоугольной рамкой
border_canvas = tk.Canvas(app, width=1000, height=200, bg="#2c003e", highlightthickness=0)
border_canvas.place(relx=0.5, rely=0.25, anchor="center")
border_rect = border_canvas.create_rectangle(10, 10, 990, 190, width=12)
title_label = tk.Label(border_canvas, text="G A M E U L T", font=("Helvetica", 100, "bold"), fg="#00ff00", bg="#2c003e")
title_label.place(relx=0.5, rely=0.5, anchor="center")

# Функция для анимации рамки вокруг плашки кнопок
button_frame_border_hue = 0
def animate_buttons_frame_border():
    global button_frame_border_hue
    rgb = colorsys.hsv_to_rgb(button_frame_border_hue, 0.7, 0.9)  # Настраиваем насыщенность и яркость
    hex_color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
    buttons_frame_border_canvas.itemconfig(button_frame_border_rect, outline=hex_color)
    button_frame_border_hue += 0.01
    if button_frame_border_hue > 1:
        button_frame_border_hue = 0
    app.after(50, animate_buttons_frame_border)

# Создаем вертикальную рамку для плашки кнопок
buttons_frame_border_canvas = tk.Canvas(app, width=230, height=300, bg="#2c003e", highlightthickness=0)
buttons_frame_border_canvas.place(relx=0.5, rely=0.65, anchor="center")
button_frame_border_rect = buttons_frame_border_canvas.create_rectangle(10, 10, 215, 290, width=12)

# Остальные функции из вашего кода для анимации и навигации по кнопкам
def highlight_selected_button():
    for i, button in enumerate(buttons):
        if i == selected_button_index:
            button.config(bg="#cce7cc", fg="black", font=("Helvetica", 20, "bold"))
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

def show_game_list():
    global ball_animation_active
    ball_animation_active = False
    background_canvas.place_forget()
    game_canvas.place(relx=0.5, rely=0.5, anchor="center")
    animate_background()
    highlight_selected_element()
    app.bind("<Up>", navigate_up)
    app.bind("<Down>", navigate_down)
    app.bind("<Return>", select_element)

def exit_app():
    app.quit()

selected_game_index = 0
def highlight_selected_element():
    for i, label in enumerate(game_labels):
        if i == selected_game_index:
            label.config(fg="#cce7cc", font=("Helvetica", 25, "bold"))
        else:
            label.config(fg="white", font=("Helvetica", 25))
    if selected_game_index == len(game_list):
        back_button.config(bg="#cce7cc", fg="black")
    else:
        back_button.config(bg="#e6e6e6", fg="black")

def navigate_up(event):
    global selected_game_index
    selected_game_index = (selected_game_index - 1) % (len(game_list) + 1)
    highlight_selected_element()

def navigate_down(event):
    global selected_game_index
    selected_game_index = (selected_game_index + 1) % (len(game_list) + 1)
    highlight_selected_element()

def select_element(event):
    if selected_game_index < len(game_list):
        selected_game = game_list[selected_game_index]
        if selected_game == "SnakeULT":
            run_snake_game()
        elif selected_game == "AgarioULT":
            run_agario_game()
        elif selected_game == "HangmanULT":
            run_hangman_game()
    else:
        hide_game_list()

def hide_game_list():
    global ball_animation_active
    ball_animation_active = True
    background_canvas.place(relx=0.5, rely=0.5, anchor="center")
    game_canvas.place_forget()
    app.unbind("<Up>")
    app.unbind("<Down>")
    app.unbind("<Return>")
    app.bind("<Up>", navigate_buttons)
    app.bind("<Down>", navigate_buttons)
    app.bind("<Return>", select_button)
    animate_elements()

hue = 0
def animate_background():
    global hue
    rgb = colorsys.hsv_to_rgb(hue, 0.5, 1)
    rgb = tuple(int(c * 255) for c in rgb)
    hex_color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    game_canvas.itemconfig(bg_rect, fill=hex_color)
    hue += 0.005
    if hue > 1:
        hue = 0
    game_canvas.after(50, animate_background)

def animate_elements():
    if not ball_animation_active:
        return

    background_canvas.delete("all")
    for ball in balls:
        ball['x'] += ball['dx']
        ball['y'] += ball['dy']
        if ball['x'] < 0 or ball['x'] > screen_width:
            ball['dx'] *= -1
        if ball['y'] < 0 or ball['y'] > screen_height:
            ball['dy'] *= -1
        background_canvas.create_oval(
            ball['x'] - ball['radius'], ball['y'] - ball['radius'],
            ball['x'] + ball['radius'], ball['y'] + ball['radius'],
            fill=ball['color'], outline=""
        )
    for snake in snakes:
        head_x, head_y = snake['segments'][0]
        new_head_x = head_x + snake['dx']
        new_head_y = head_y + snake['dy']
        snake['segments'] = [(new_head_x, new_head_y)] + snake['segments'][:-1]
        if new_head_x < 0 or new_head_x > screen_width:
            snake['dx'] *= -1
        if new_head_y < 0 or new_head_y > screen_height:
            snake['dy'] *= -1
        for i, (x, y) in enumerate(snake['segments']):
            color = f"#{int(255 - i * 12):02x}{int(i * 12):02x}{random.randint(100, 255):02x}"
            background_canvas.create_oval(
                x - snake['radius'], y - snake['radius'],
                x + snake['radius'], y + snake['radius'],
                fill=color, outline=""
            )

    app.after(50, animate_elements)

def run_snake_game():
    exe_path = r"C:\ourgamesproject\dist\snakeult.exe"  # Замените на реальный полный путь
    print("Attempting to launch:", exe_path)  # Диагностический вывод пути
    try:
        subprocess.Popen([exe_path], shell=True)
    except FileNotFoundError as e:
        print(f"File {exe_path} not found. Error: {e}")

def run_hangman_game():
    exe_path = r"C:\ourgamesproject\dist\hangmanult.exe"  # Замените на реальный полный путь
    print("Attempting to launch:", exe_path)  # Диагностический вывод пути
    try:
        subprocess.Popen([exe_path], shell=True)
    except FileNotFoundError as e:
        print(f"File {exe_path} not found. Error: {e}")

def run_agario_game():
    # Укажите абсолютный путь к `agarioult.exe`
    exe_path = r"C:\ourgamesproject\dist\agarioult.exe"  # Замените на реальный полный путь
    print("Attempting to launch:", exe_path)  # Диагностический вывод пути
    try:
        subprocess.Popen([exe_path], shell=True)
    except FileNotFoundError as e:
        print(f"File {exe_path} not found. Error: {e}")

# Инициализация анимации шаров и змей
for _ in range(num_balls):
    balls.append({
        'x': random.randint(0, screen_width),
        'y': random.randint(0, screen_height),
        'dx': random.choice([-ball_speed, ball_speed]),
        'dy': random.choice([-ball_speed, ball_speed]),
        'radius': random.randint(10, 30),
        'color': "#%02x%02x%02x" % (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    })

for _ in range(num_snakes):
    segments = [(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(10)]
    dx = random.choice([-snake_speed, snake_speed])
    dy = random.choice([-snake_speed, snake_speed])
    snakes.append({
        'segments': segments,
        'dx': dx,
        'dy': dy,
        'radius': 10
    })

# Инициализация кнопок и интерфейса
frame = tk.Frame(buttons_frame_border_canvas, bg="#2c003e")
frame.place(relx=0.5, rely=0.5, anchor="center")

play_button = tk.Button(frame, text="Играть", command=show_game_list, font=("Helvetica", 20, "bold"),
                        fg="black", bg="#e6e6e6", activebackground="#cccccc", borderwidth=10)
play_button.pack(pady=20, ipadx=20, ipady=10)

exit_button = tk.Button(frame, text="Выйти", command=exit_app, font=("Helvetica", 20, "bold"),
                        fg="black", bg="#e6e6e6", activebackground="#cccccc", borderwidth=10)
exit_button.pack(pady=20, ipadx=20, ipady=10)

buttons.extend([play_button, exit_button])
highlight_selected_button()

app.bind("<Up>", navigate_buttons)
app.bind("<Down>", navigate_buttons)
app.bind("<Return>", select_button)

game_canvas = tk.Canvas(app, width=1200, height=700, bg="#2c003e", highlightthickness=0)
game_canvas.place_forget()

corner_radius = 50
bg_rect = game_canvas.create_rectangle(corner_radius, 0, 1200 - corner_radius, 700, fill="#2c003e", outline="")
game_canvas.create_rectangle(0, corner_radius, 1200, 700 - corner_radius, fill="#2c003e", outline="")

game_canvas.create_oval(0, 0, corner_radius * 2, corner_radius * 2, fill="#2c003e", outline="")
game_canvas.create_oval(1200 - corner_radius * 2, 0, 1200, corner_radius * 2, fill="#2c003e", outline="")
game_canvas.create_oval(0, 700 - corner_radius * 2, corner_radius * 2, 700, fill="#2c003e", outline="")
game_canvas.create_oval(1200 - corner_radius * 2, 700 - corner_radius * 2, 1200, 700, fill="#2c003e", outline="")

game_header = tk.Label(game_canvas, text="Во что сыграем?", font=("Helvetica", 40, "bold"), bg="#2c003e", fg="white")
game_header.place(relx=0.5, rely=0.15, anchor="center")

# Обновленный список игр
game_list = ["AgarioULT", "SnakeULT", "HangmanULT"]
game_labels = []

for i, game in enumerate(game_list):
    game_label = tk.Label(game_canvas, text=game, font=("Helvetica", 25), fg="white", bg="#2c003e")
    game_label.place(relx=0.5, rely=0.3 + i * 0.15, anchor="center")
    game_labels.append(game_label)

back_button = tk.Button(game_canvas, text="Назад", command=hide_game_list, font=("Helvetica", 20, "bold"),
                        fg="black", bg="#e6e6e6", activebackground="#cccccc", borderwidth=10)
back_button.place(relx=0.505, rely=0.80, anchor="center")

# Запуск анимаций
animate_button_colors()
animate_elements()
animate_border()
animate_buttons_frame_border()
app.mainloop()
