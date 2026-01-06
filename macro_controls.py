import pyautogui
import time
import keyboard



        

def time_to_start(stop_event=None):
    """Countdown with optional stop event checking"""
    for i in range(5):
        if stop_event and stop_event.is_set():
            print("Start cancelled by user")
            return
        print(5-i)
        # Check stop event during sleep
        if stop_event:
            for _ in range(10):
                if stop_event.is_set():
                    print("Start cancelled by user")
                    return
                time.sleep(0.1)
        else:
            time.sleep(1)

def click():
    pyautogui.click()
    time.sleep(0.2)  # Reduced from 0.5s - enough time for click to register
    # Press Enter 5 times quickly to ensure it registers
    for _ in range(5):
        pyautogui.press('enter')
        time.sleep(0.03)  # Reduced from 0.05s - still enough for key press to register


def click_reset_button(window_name, reset_pos):
    """
    Click the Reset button at the given window-relative coordinates.
    
    Args:
        window_name: Name of the window (e.g., "Maplestory")
        reset_pos: Tuple (x, y, width, height) in window coordinates
    """
    import win32gui
    
    if reset_pos is None:
        print("ERROR: Reset button position not available")
        return False
    
    reset_x, reset_y, reset_w, reset_h = reset_pos
    
    # Find window handle
    hwnd = win32gui.FindWindow(None, window_name)
    if not hwnd:
        print(f"ERROR: Window '{window_name}' not found")
        return False
    
    # Get window rectangle (screen coordinates)
    window_rect = win32gui.GetWindowRect(hwnd)
    if not window_rect:
        print(f"ERROR: Failed to get window rectangle for '{window_name}'")
        return False
    
    # Calculate screen coordinates
    # Window rect is (left, top, right, bottom)
    window_left = window_rect[0]
    window_top = window_rect[1]
    
    # Reset button center position in screen coordinates
    # Note: window coordinates start at (0,0) inside the window
    # Screen coordinates = window position + window-relative position
    screen_x = window_left + reset_x + (reset_w // 2)
    screen_y = window_top + reset_y + (reset_h // 2)
    
    # Move mouse to Reset button and click
    # Use duration=0.1 for faster movement (still smooth enough)
    pyautogui.moveTo(screen_x, screen_y, duration=0.1)
    time.sleep(0.05)  # Reduced delay - enough for cursor to be in place
    pyautogui.click()
    time.sleep(0.2)  # Reduced from 0.5s - enough time for click to register
    
    # Press Enter 5 times quickly to ensure it registers
    for _ in range(5):
        pyautogui.press('enter')
        time.sleep(0.03)  # Reduced from 0.05s - still enough for key press to register
    
    return True


