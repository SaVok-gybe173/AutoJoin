import win32gui
import win32con

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"  # Сбрасываем цвет

def get_all_windows():
    """Возвращает список всех видимых окон с заголовками."""
    windows = []

    def enum_callback(hwnd, _):
        # Проверяем, что окно видимо и имеет заголовок
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append((hwnd, title))

    win32gui.EnumWindows(enum_callback, None)
    return windows

print(f"{GREEN}[+]{RESET} Поиск окна...\n")

all_windows = get_all_windows()
for hwnd, title in all_windows:
    print(f"HWND: {hwnd}, Title: {title}")