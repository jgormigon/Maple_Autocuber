from numpy import true_divide
import pyautogui
import keyboard
import time
while keyboard.is_pressed('q')==False:
    time.sleep(3)
    pyautogui.press('z')
    time.sleep(0.1)