import pyautogui
import keyboard
import time
def autoclicker():
    time.sleep(3)
    while keyboard.is_pressed('q')==False:
        pyautogui.click()

def clicker():
    while keyboard.is_pressed('q')==False:
        if keyboard.is_pressed('left_ctrl')==True:
            pyautogui.click()
            time.sleep(0.1)
            pyautogui.press('enter')

clicker()