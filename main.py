from pynput.mouse import Button, Controller
from pyfiglet import Figlet
from rich.highlighter import Highlighter
from rich.console import Console
from termcolor import cprint
from typing import TypedDict

import re
import win32gui
import win32process

class TypedDictInfoProcess(TypedDict):
    title: str
    hwnd: int
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
                    'class': class_name,
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
            users.append({"hwnd": win['hwnd'], "server": mass[-2], "user": mass[-1], "title": win['title'], "pid": win["pid"]})
            
    if len(users) == 0:
        print("{RED}[-]{RESET} Не найден ни одино активное окно")
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

