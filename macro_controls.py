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


def press_reset_spacebar():
    """
    Press spacebar to reset (replaces clicking the Reset button).
    This is faster and more reliable than moving the mouse and clicking.
    """
    # Press spacebar to reset
    keyboard.press_and_release('space')
    time.sleep(0.1)  # Brief delay to ensure key press registers
    
    # Press Enter 5 times quickly to ensure it registers
    for _ in range(5):
        # pyautogui.press('enter')
        keyboard.press_and_release('space')
        time.sleep(0.03)  # Reduced from 0.05s - still enough for key press to register
    time.sleep(0.5)
    return True


