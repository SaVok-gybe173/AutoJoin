import ctypes
from ctypes import wintypes
import time

# Структуры для SendInput
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [("type", wintypes.DWORD), ("union", _INPUT)]

def send_input_click(x=None, y=None):
    if not (x is None or y is None):
        ctypes.windll.user32.SetCursorPos(x, y)
        time.sleep(0.01)

    # Создаем события для нажатия и отпускания
    extra = ctypes.pointer(wintypes.ULONG(0))
    click_down = INPUT()
    click_down.type = INPUT_MOUSE
    click_down.union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, extra)

    click_up = INPUT()
    click_up.type = INPUT_MOUSE
    click_up.union.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, extra)

    # Отправляем события
    ctypes.windll.user32.SendInput(1, ctypes.byref(click_down), ctypes.sizeof(INPUT))
    time.sleep(0.05)
    ctypes.windll.user32.SendInput(1, ctypes.byref(click_up), ctypes.sizeof(INPUT))