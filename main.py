from config import *
from pynput.mouse import Button, Controller
from PIL import Image

import win32gui
import win32ui
import win32con
import keyboard
import win32process
import importlib
import importlib.util
import pyautogui
import time
import os

def import_lib(name: str) -> None:
    global IMPORTMODUL, user, MAIN_PATH
    file = os.path.join(MAIN_PATH, user["server"], "lib", f"{name}.py")
    if not os.path.isfile(file):
        with open(file, 'w', encoding="utf-8") as f:
            f.write('')
    try:
        spec = importlib.util.spec_from_file_location("POSITION1", file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, name)
    except Exception as e:
        print(f"{RED}[-]{RESET} Не удалось загрузить модуль")

def loads_lib():
    IMPORTMODUL


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
    rect = win32gui.GetClientRect(hwnd)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

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
        print("PrintWindow не удалась, возможно, окно не поддерживает эту операцию.")

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
        try:
            img = capture_window_printwindow(hwnd)
            if img:
                img.save("screenshot.png")
            if _is:
                minimize_back(hwnd)
        except Exception as e:
            print(f"{RED}[-]{RESET} Ошибка {e.__class__}: {e}")
class Working:
    mouse = Controller()
    stop_flag = True
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

    def click_pos1(self):
        self.mouse.position = position1
        time.sleep(self.time)
        self.mouse.click(Button.left, config.getint("POSITION1", "count", fallback=1), )
        time.sleep(self.time)

    def click_pos2(self):
        self.mouse.position = position2
        time.sleep(self.time)
        self.mouse.click(Button.left, config.getint("POSITION2", "count", fallback=1))
        time.sleep(self.time)

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
                pass

def main():
    global MAIN_PATH
    if not os.path.isdir(MAIN_PATH): os.mkdir(MAIN_PATH)
    console()
    print()

    updatePath()
    updateUser()

    loads()
    
    scrin()

if __name__ == "__main__":
    main()