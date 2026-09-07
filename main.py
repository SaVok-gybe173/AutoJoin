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
import win32process
import pyautogui
import re
import time
import ctypes
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


RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"  # Сбрасываем цвет

console = Console(highlighter=MoneyHighlighter())
flr = Figlet(font='slant')  # Более стильный шрифт
ascii_art = flr.renderText("AutoJoin GribLand")
console.print(ascii_art, style="bold green")
print(f"{GREEN}[+]{RESET} GitHub: {BLUE}https://github.com/SaVok-gybe173{RESET}")
print(f"{GREEN}[+]{RESET} {BLUE}https://github.com/SaVok-gybe173/AutoJoin{RESET}")

users: list[TypedDictInfoProcess] = []  # список окон с Gribland
user: int = 0                           # Индекс

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
        print(f"{RED}[-]{RESET} Не найден ни одино активное окно")
    elif len(users) == 1:
        print()
        user = 0
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

            user = num-1
            print(f"{GREEN}[+]{RESET} Выбран игрок {users[num]['user']} на сервере {users[num]['server']}, HWND:{users[num]['hwnd']}")
            break

updateUsers()

def turnaround(hwnd) -> None:
    # Если окно свёрнуто — разворачиваем
    if win32gui.IsIconic(hwnd):
        print("Окно свёрнуто, разворачиваю...")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)   # SW_RESTORE = 9
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)  # даём время на отрисовку (можно увеличить до 0.5)
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
    hwnd = win32gui.FindWindow(users[0]['_class'], users[0]['title'])
    if hwnd == 0:
        print(f"{RED}[-]{RESET} Окно не найдено")
        updateUsers()
    else:
        _is = turnaround(hwnd)
        img = capture_window_printwindow(hwnd)
        img.save("screenshot_window.png")
        if _is:
            minimize_back(hwnd)
scrin()