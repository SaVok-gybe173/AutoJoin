from typing import TypedDict
from rich.highlighter import Highlighter
from pyfiglet import Figlet
from rich.console import Console
from termcolor import cprint

import configparser
import ctypes
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

screenshot_save = True

#x: int | None = None
#y: int | None = None

#width: int | None = None
#height: int | None = None

users: list[TypedDictInfoProcess] = []  # список окон с Gribland
user: MoneyHighlighter | None = None    # пользователь

config_name = "settings.ini"
config = configparser.ConfigParser()

config_standart = """
[SETTINGS]
time_turnaround = 0.3
time = 0.1      // время после каждой операции
start_stop = 1  // кнопка для запуска/остановки
is_save = yes   // работа изменение кординат
stop = f7       // экстренная остановка

[POSITION1] // начало играть
x = 0.5 // кординаты
y = 0.5
count = 1 // количество нажатий
key = 8

[POSITION2]
x = 0.4 // кординаты
y = 0.4
count = 1 // количество нажатий
key = 9
"""

# Модули для кастомизации
IMPORTMODUL_LIST = [
    "POSITION1",
    "POSITION2",
    "POSITION3"
]

IMPORTMODUL = {

}
IMPORTMODUL_COD = {
    "POSITION1":
    """
from config import *
from main import *

def POSITION1(self: Working):
    global config
    time.sleep(self.time)
    self.mouse.click(Button.left, config.getint("POSITION1", "count", fallback=1), )
    time.sleep(self.time)
""",
    "POSITION2":
    """
from config import *
from main import *

def POSITION2(self: Working):
    global config
    time.sleep(self.time)
    self.mouse.click(Button.left, config.getint("POSITION1", "count", fallback=1), )
    time.sleep(self.time)
"""
}

def console():
    console = Console(highlighter=MoneyHighlighter())
    flr = Figlet(font='slant')  # Более стильный шрифт
    ascii_art = flr.renderText("AutoJoin GribLand")
    console.print(ascii_art, style="bold green")
    print(f"{GREEN}[+]{RESET} GitHub: {BLUE}https://github.com/SaVok-gybe173{RESET}")
    print(f"{GREEN}[+]{RESET} {BLUE}https://github.com/SaVok-gybe173/AutoJoin{RESET}")
    print(f"{GREEN}[+]{RESET} Скрипт для автоматического захода на сервера GribLand")