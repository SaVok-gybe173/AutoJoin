from pynput.mouse import Button, Controller
from pyfiglet import Figlet
from rich.highlighter import Highlighter
from rich.console import Console
from termcolor import cprint
from typing import TypedDict
from PIL import Image

import win32gui
import win32ui
import win32con
import keyboard
import configparser
import win32process
import pyautogui
import ctypes
import time
import re
import os
try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass   # для старых Windows можно использовать SetProcessDPIAwareness

class TypedDictInfoProcess(TypedDict):
    title: str
    hwnd: int
    _class: str
    pid: int

    server: str
    user: str

class MoneyHighlighter(Highlighter):
    def highlight(self, text):
        for match in re.finditer(r'/', text.plain):
            text.stylize("bold blue", match.start(), match.end())
        for match in re.finditer(r'\\', text.plain):
            text.stylize("bold blue", match.start(), match.end())

MAIN_PATH = 'data'

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"  # Сбрасываем цвет

users: list[TypedDictInfoProcess] = []  # список окон с Gribland
user: MoneyHighlighter | None = None    # пользователь

config_name = "settings.ini"
config = configparser.ConfigParser()

config_standart = """
[SETTINGS]
time_turnaround = 0.3
time = 0.05     // время после каждой операции
start_stop = 1  // кнопка для запуска/остановки
position1 = 8   // кнопка для настройки начальной позиции
position2 = 9   // кнопка для настройки конечно позиции
stop = f7       // экстренная остановка
alignment = 2   // для выравнивание

[POSITION1]
time = 0.1
    // кординаты
x = 0.5
y = 0.5
count = 1 // количество нажатий

[POSITION2]
time = 0.1
    // кординаты
x = 0.4
y = 0.4
count = 1 // количество нажатий

"""

def loads():
    global config, config_name, config_standart
    if not os.path.isfile(config_name):
        with open(config_name, 'w', encoding='utf-8') as f: f.write(config_standart)
    config.read(config_name, "utf-8")
    

def get_detailed_windows() -> list[TypedDictInfoProcess]:
    """Возвращает список окон с их HWND, заголовком, классом и PID процесса."""
    windows = []

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                class_name = win32gui.GetClassName(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    '_class': class_name,
                    'pid': pid
                })

    win32gui.EnumWindows(enum_callback, None)
    return windows

def updateUsers():
    """
    Обновеление списка серверов
    """
    global users, user
    print(f"{GREEN}[+]{RESET} Поиск окна...\n")
    users.clear()
    for win in get_detailed_windows():
        title: str = win['title'].replace(' ', '')
        if len(mass := title.split('|')) == 3 and mass[0] == "GribLand":
            print(f"{GREEN}[+]{RESET} Найден игрок {mass[-1]} на сервере {mass[-2]}, HWND:{win['hwnd']}")
            users.append({"hwnd": win['hwnd'], "server": mass[-2], "user": mass[-1], "title": win['title'], "pid": win["pid"], "_class": win['_class']})
    if len(users) == 0:
            print(f"{RED}[-]{RESET} Не найден ни одного активного окна")

def updateUser():
    global user, users
    updateUsers()
    if len(users) == 0:
        user = None
    elif len(users) == 1:
        print()
        user = users[0]
    else:
        while True:
            print()
            print(f"{GREEN}[+]{RESET} Найдено несколько окон, подалуйста введите номер окна...")
            for i, win in enumerate(users):
                print(f"{BLUE}[+]{RESET} {i+1}. Сервер {win['server']}, игрок {win['user']}.")
            num = input(f"{YELLOW}[+]{RESET} Число: ")
            try:
                num = int(num)
                if len(users) < num:
                    continue
            except:
                continue

            user = users[num-1]
            print(f"{GREEN}[+]{RESET} Выбран игрок {users[num]['user']} на сервере {users[num]['server']}, HWND:{users[num]['hwnd']}")
            break

def updatePath():
    global users, MAIN_PATH

    dirs = set()
    for i in users:
        dirs.add(i['server'])

    for i in dirs:
        server = os.path.join(MAIN_PATH, "i")
        if not os.path.isdir(server): os.mkdir(server)
        if not os.path.isdir(imej := os.path.join(server, "imeg")): os.mkdir(imej)
        if not os.path.isdir(logs := os.path.join(server, "logs")): os.mkdir(logs)


def turnaround(hwnd) -> None:
    # Если окно свёрнуто — разворачиваем
    if win32gui.IsIconic(hwnd):
        print("Окно свёрнуто, разворачиваю...")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)   # SW_RESTORE = 9
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)  # даём время на отрисовку
        return True
    return False

def minimize_back(hwnd):
    """Сворачивает окно."""
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def capture_window_printwindow(hwnd):
    rect = win32gui.GetClientRect(hwnd)
    left, top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    right, bottom = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
    width = right - left
    height = bottom - top
    return pyautogui.screenshot(region=(left, top, width, height))


def scrin():
    global users, user
    if not users:
        return
    hwnd = win32gui.FindWindow(user['_class'], user['title'])
    if hwnd == 0:
        print(f"{RED}[-]{RESET} Окно не найдено")
        updateUsers()
    else:
        _is = turnaround(hwnd)
        img = capture_window_printwindow(hwnd)
        img.save("screenshot_window.png")
        if _is:
            minimize_back(hwnd)

class Working:
    mouse = Controller()

    def alignment():
        global stop_flag
        stop_flag = True
        mouse.press(Button.left)
        time.sleep(_time)
        mouse.position = position1
        time.sleep(_time)
        mouse.release(Button.left)
        print(f"Клавиша {key_alignment} нажата, выравнивание...")
        keyboard.add_hotkey(key_alignment, alignment)

    def _POSITION2(self):
        global position2
        position2 = self.mouse.position
        config.set('POSITION2', 'x', str(position2[0]))
        config.set('POSITION2', 'y', str(position2[1]))
        print(f"Клавиша {config.get("POSITION2", "key", fallback="9")} нажата...")
    keyboard.add_hotkey(config.get("POSITION2", "key", fallback="9"), _POSITION2)

    def _POSITION1(self):
        global position1
        position1 = self.mouse.position
        config.set('POSITION1', 'x', str(position1[0]))
        config.set('POSITION1', 'y', str(position1[1]))
        print(f"Клавиша {config.get("POSITION1", "key", fallback="8")} нажата...")
    keyboard.add_hotkey(config.get("POSITION1", "key", fallback="8"), _POSITION1)

    def on_esc():
        global while_flag
        while_flag = not while_flag
        print(f"Клавиша {config.get("POSITION1", "key", fallback="8")} нажата, останавливаем...")
    keyboard.add_hotkey(config.get("POSITION1", "key", fallback="8"), on_esc)

    def on_start():
        global stop_flag
        stop_flag = not stop_flag
        print(f"Клавиша {start_stop} нажата...")
    keyboard.add_hotkey(start_stop, on_start)

    def start(self):
        global config

        while while_flag:
            _time = config.getfloat("SETTINGS", "time", fallback=0.1)
            if not stop_flag:
                self.mouse.position = position1
                time.sleep(_time)
                self.mouse.click(Button.left, count1)
                time.sleep(_time)
                
                self.mouse.position = position2
                time.sleep(_time)
                self.mouse.click(Button.left, count2)
                time.sleep(_time)

def main():
    global MAIN_PATH
    if not os.path.isdir(MAIN_PATH): os.mkdir(MAIN_PATH)
    loads()

    console = Console(highlighter=MoneyHighlighter())
    flr = Figlet(font='slant')  # Более стильный шрифт
    ascii_art = flr.renderText("AutoJoin GribLand")
    console.print(ascii_art, style="bold green")
    print(f"{GREEN}[+]{RESET} GitHub: {BLUE}https://github.com/SaVok-gybe173{RESET}")
    print(f"{GREEN}[+]{RESET} {BLUE}https://github.com/SaVok-gybe173/AutoJoin{RESET}")
    print(f"{GREEN}[+]{RESET} Скрипт для автоматического захода на сервера GribLand")

    updateUsers()

    scrin()

if __name__ == "__main__":
    main()