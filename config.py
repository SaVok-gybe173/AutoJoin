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
time = 0.1      
start_stop = 1  
is_save = yes
stop = f7
home = no

[POSITION1]
x = 0.3
y = 0.45
key = 8
percent = 80
modul = POSITION1

[POSITION2]
x = 0.4
y = 0.45
key = 9
percent = 80
modul = POSITION2

[POSITION3]
x = 0.5
y = 0.6
key = 0
percent = 80
modul = POSITION3 

[NOME]
comand = /home
modul = NOME
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
from SendInput import send_input_click

def POSITION1(self: Working, x, y, width, height):
    global config
    time.sleep(self.time)
    self.mouse.position = (x+config.getfloat("POSITION1", "x", fallback=0.3)*width, y+config.getfloat("POSITION1", "y", fallback=0.45)*height)
    time.sleep(self.time+1)
    send_input_click()
    time.sleep(self.time+1)
""",
    "POSITION2":
    """
from config import *
from main import *
from SendInput import send_input_click

def POSITION2(self: Working, x, y, width, height):
    global config
    time.sleep(self.time)
    self.mouse.position = (x+config.getfloat("POSITION2", "x", fallback=0.4)*width, y+config.getfloat("POSITION2", "y", fallback=0.45)*height)
    time.sleep(self.time)
    send_input_click()
    time.sleep(self.time)
""",
    "POSITION3":
    """
from config import *
from main import *
from SendInput import send_input_click

def POSITION3(self: Working, x, y, width, height):
    global config
    time.sleep(self.time)
    self.mouse.position = (x+config.getfloat("POSITION3", "x", fallback=0.5)*width, y+config.getfloat("POSITION3", "y", fallback=0.6)*height)
    time.sleep(self.time)
    send_input_click()
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