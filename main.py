import win32gui
import win32con

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

# Получаем и выводим список окон
all_windows = get_all_windows()
for hwnd, title in all_windows:
    print(f"HWND: {hwnd}, Title: {title}")