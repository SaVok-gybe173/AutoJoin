from config import *
from pynput.mouse import Button, Controller
from PIL import Image
from typing import Callable

import numpy as np
import win32gui
import win32ui
import win32con
import keyboard
import struct
import win32process
import importlib
import importlib.util
import pyautogui
import time
import os

def null(self: "Working", x, y, width, height) -> None:
    pass

def import_lib(name: str) -> Callable:
    global IMPORTMODUL_COD, IMPORTMODUL, user, MAIN_PATH
    file = os.path.join(MAIN_PATH, user["server"], "lib", f"{name}.py")
    if not os.path.isfile(file):
        with open(file, 'w', encoding="utf-8") as f:
            if name in IMPORTMODUL_COD:
                f.write(IMPORTMODUL_COD[name])
            else:
                f.write('''
from config import *\n
from main import *\n
\n
def null(self: Warning, x, y, width, height) -> None:\n
    pass\n
''')
    try:
        spec = importlib.util.spec_from_file_location(name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"{GREEN}[+]{RESET} Модуль {name} успешно загружен ")
        return getattr(module, name)
    except Exception as e:
        print(f"{RED}[-]{RESET} [{os.path.isfile(file)}]Не удалось загрузить модуль {file} is type {e.__class__}: {e}")
        return null

def loads_lib() -> None:
    global IMPORTMODUL_LIST, config, IMPORTMODUL
    for imp in IMPORTMODUL_LIST:
        IMPORTMODUL[imp] = import_lib(config.get(imp, "modul", fallback=imp))


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
        print(f"\n{BLUE}[-]{RESET} Запустите GribLand...")
        while True:
            updateUsers()
            if len(users) == 0:
                time.sleep(5)
            #else:
                #print(f"{GREEN}[+]{RESET}")
            else:
                user = users[0]
                print(f"{GREEN}[+]{RESET} Выбран игрок {users[num]['user']} на сервере {users[num]['server']}, HWND:{users[num]['hwnd']}")
                break
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
        server = os.path.join(MAIN_PATH, i)
        if not os.path.isdir(server): os.mkdir(server)
        if not os.path.isdir(imej := os.path.join(server, "imeg")): os.mkdir(imej)
        if not os.path.isdir(logs := os.path.join(server, "logs")): os.mkdir(logs)
        if not os.path.isdir(lib := os.path.join(server, "lib")): os.mkdir(lib)
        if not os.path.isfile(POSITION1 := os.path.join(server, "POSITION1.png")):
            with open(POSITION1, 'w+b') as f:
                f.write(b"")

def turnaround(hwnd) -> None:
    global config
    # Если окно свёрнуто — разворачиваем
    if win32gui.IsIconic(hwnd):
        print(f"{GREEN}[+]{RESET} Окно свёрнуто, разворачиваю...")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)   # SW_RESTORE = 9
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(config.getfloat("SETTINGS", "time_turnaround", fallback=0.4))  # даём время на отрисовку
        return True
    return False

def minimize_back(hwnd):
    """Сворачивает окно."""
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def capture_window_printwindow(hwnd):
    # Получаем размеры клиентской области окна
    window_rect = win32gui.GetWindowRect(hwnd)
    width = window_rect[2] - window_rect[0]
    height = window_rect[3] - window_rect[1]

    # Создаём контекст устройства для окна
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    # Создаём совместимый DC для рисования в памяти
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # Создаём битмап нужного размера
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    # Используем PrintWindow для принудительной отрисовки окна в наш DC
    # Флаг PW_CLIENTONLY = 0x00000001 означает, что рисуем только клиентскую область
    result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0x00000001)
    if result == 0:
        print(f"{RED}[-]{RESET} PrintWindow не удалась, возможно, окно не поддерживает эту операцию.")

    # Конвертируем битмап в PIL Image
    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

    # Освобождаем ресурсы
    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    return img

def image_similarity_percent(img1: Image.Image, img2: Image.Image) -> float:
    """
    Сравнивает два PIL.Image объекта и возвращает процент их совпадения.

    Аргументы:
        img1 (PIL.Image): первое изображение
        img2 (PIL.Image): второе изображение

    Возвращает:
        float: процент схожести (0.0 – 100.0)
    """
    # Проверка на None
    if img1 is None or img2 is None:
        raise ValueError("Изображения не должны быть None")

    # Получаем размеры
    w1, h1 = img1.size
    w2, h2 = img2.size

    # Если размеры разные, приводим оба к размеру первого изображения
    # (можно выбрать любой другой способ, например, к минимальному размеру)
    if (w1, h1) != (w2, h2):
        # resample=Image.LANCZOS даёт лучшее качество при изменении размера
        img2 = img2.resize((w1, h1), Image.LANCZOS)
        # При необходимости можно также изменить и первое, если хотите другой общий размер
        # img1 = img1.resize((w1, h1), Image.LANCZOS)

    # Конвертируем в оттенки серого для упрощения сравнения
    gray1 = img1.convert('L')
    gray2 = img2.convert('L')

    # Преобразуем в массивы numpy
    arr1 = np.array(gray1, dtype=np.float32)
    arr2 = np.array(gray2, dtype=np.float32)

    # Вычисляем среднюю абсолютную разницу (MAD)
    mad = np.mean(np.abs(arr1 - arr2))

    # Переводим в процент совпадения: 100% при mad=0, 0% при mad=255
    similarity = max(0.0, 100.0 * (1.0 - mad / 255.0))

    return similarity

def get_window_rect_real(hwnd):
    # Используем GetWindowInfo (работает даже для свёрнутых)
    try:
        from ctypes import windll, c_int, byref, sizeof, create_string_buffer
        WINDOWINFO = create_string_buffer(60)
        windll.user32.GetWindowInfo(hwnd, byref(WINDOWINFO))
        # парсим структуру (смещения: rcWindow начинается с 20 байта)
        rect = struct.unpack('llll', WINDOWINFO[20:36])
        return rect  # (left, top, right, bottom)
    except:
        return None


def scrin():
    global users, user, config, x, y, width, height, MAIN_PATH, work, IMPORTMODUL
    if not users:
        return

    hwnd = win32gui.FindWindow(user['_class'], user['title'])

    if hwnd == 0:
        print(f"{RED}[-]{RESET} Окно не найдено")
        updateUsers()
    else:
        try:
            _is = turnaround(hwnd)
            rect = get_window_rect_real(hwnd)
            if rect:
                x, y = rect[0], rect[1]
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]

            #print(width, height, normal_rect)
            img = capture_window_printwindow(hwnd)
            if config.getboolean("SETTINGS", "is_save", fallback=False):
                img.save("screenshot.png")
            
            if (pr := image_similarity_percent(img, Image.open(os.path.join(MAIN_PATH, user["server"], f"{config.get("POSITION3", "modul", fallback="POSITION3")}.png")))) >= config.getint("POSITION3", "percent", fallback=90):
                IMPORTMODUL[config.get("POSITION3", "modul", fallback="POSITION3")](work, x, y, width, height)
                IMPORTMODUL[config.get("POSITION1", "modul", fallback="POSITION1")](work, x, y, width, height)
                IMPORTMODUL[config.get("POSITION2", "modul", fallback="POSITION2")](work, x, y, width, height)
                print(f"{BLUE}[+]{RESET} Совпадение: {pr}%")

            if (pr := image_similarity_percent(img, Image.open(os.path.join(MAIN_PATH, user["server"], f"{config.get("POSITION1", "modul", fallback="POSITION1")}.png")))) >= config.getint("POSITION1", "percent", fallback=90):
                IMPORTMODUL[config.get("POSITION1", "modul", fallback="POSITION1")](work, x, y, width, height)
                IMPORTMODUL[config.get("POSITION2", "modul", fallback="POSITION2")](work, x, y, width, height)
                print(f"{BLUE}[+]{RESET} Совпадение: {pr}%")

            if _is:
                minimize_back(hwnd)
        except Exception as e:
            print(f"{RED}[-]{RESET} Ошибка {e.__class__}: {e}")

class Working:
    mouse = Controller()
    stop_flag = False
    while_flag = True

    def __init__(self):
        self.time = config.getfloat("SETTINGS", "time", fallback=0.1)


    def _POSITION2(self):
        global position2
        position2 = self.mouse.position
        config.set('POSITION2', 'x', str(position2[0]))
        config.set('POSITION2', 'y', str(position2[1]))
        print(f"{GREEN}[+]{RESET} Клавиша {config.get("POSITION2", "key", fallback="9")} нажата...")
    keyboard.add_hotkey(config.get("POSITION2", "key", fallback="9"), _POSITION2)

    def _POSITION1(self):
        global position1
        position1 = self.mouse.position
        config.set('POSITION1', 'x', str(position1[0]))
        config.set('POSITION1', 'y', str(position1[1]))
        print(f"{GREEN}[+]{RESET} Клавиша {config.get("POSITION1", "key", fallback="8")} нажата...")
    keyboard.add_hotkey(config.get("POSITION1", "key", fallback="8"), _POSITION1)

    def on_esc(self):
        self.while_flag = not self.while_flag
        print(f"{GREEN}[+]{RESET} Клавиша {config.get("SETTINGS", "stop", fallback="8")} нажата, останавливаем...")
    keyboard.add_hotkey(config.get("SETTINGS", "stop", fallback="8"), on_esc)

    def on_start(self):
        self.stop_flag = not self.stop_flag
        print(f"{GREEN}[+]{RESET} Клавиша {config.get("SETTINGS", "stop", fallback="8")} нажата, работа: {not self.stop_flag}... ")
    keyboard.add_hotkey(config.get("SETTINGS", "stop", fallback="8"), on_start)

    def start(self):
        global config

        while self.while_flag:
            if not self.stop_flag:
                scrin()
                time.sleep(120)

def main():
    global MAIN_PATH, config, work
    if not os.path.isdir(MAIN_PATH): os.mkdir(MAIN_PATH)
    console()
    print()

    updateUser()
    updatePath()

    loads()
    loads_lib()
    print(f"{f'{BLUE}[+]' if config.getboolean("SETTINGS", "home", fallback=False) else f'{YELLOW}[-]'}{RESET} Замена настроек: {config.getboolean("SETTINGS", "home", fallback=False)}")

    work = Working()
    work.start()

if __name__ == "__main__":
    main()