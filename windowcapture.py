import imghdr
import cv2 as cv
import numpy as np
import os
from time import time
import win32gui, win32ui, win32con
import pyautogui

# Try to import mss for better capture on Windows 10+
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))



class WindowCapture:

    w = 0
    h = 0 
    hwnd = None
    window_name = None
    sct = None  # mss screenshot object
    
    def __init__(self,window_name):
        self.window_name = window_name
        self.hwnd = win32gui.FindWindow(None, window_name)

        if not self.hwnd: 
            error_msg = (
                f"ERROR: Window '{window_name}' not found!\n\n"
                f"Please make sure:\n"
                f"1. The window is open and visible\n"
                f"2. The window name matches exactly (case-sensitive)\n"
                f"3. Check the window title bar for the exact name\n\n"
                f"Tip: You can change the window name in image_finder.py line 14"
            )
            raise Exception(error_msg)

        # Get the full window dimensions
        try:
            window_rect = win32gui.GetWindowRect(self.hwnd)
        except Exception as e:
            raise Exception(f"ERROR: Failed to get window rectangle for '{window_name}'. Error: {str(e)}")
        
        if window_rect is None:
            raise Exception(f"ERROR: GetWindowRect returned None for '{window_name}'. This may happen with certain browser windows.")
        
        if not isinstance(window_rect, (tuple, list)) or len(window_rect) < 4:
            raise Exception(f"ERROR: Invalid window rectangle format for '{window_name}'. Got: {window_rect}")
        
        try:
            self.w = window_rect[2] - window_rect[0]  # width = right - left
            self.h = window_rect[3] - window_rect[1]   # height = bottom - top
        except (IndexError, TypeError) as e:
            raise Exception(f"ERROR: Failed to calculate window dimensions for '{window_name}'. Rectangle: {window_rect}, Error: {str(e)}")
        
        if self.w <= 0 or self.h <= 0:
            raise Exception(f"ERROR: Invalid window dimensions ({self.w}x{self.h}) for '{window_name}'. Window may be minimized or invalid.")
        
        # Initialize mss if available (better for Windows 10+)
        if MSS_AVAILABLE:
            try:
                self.sct = mss.mss()
            except Exception:
                self.sct = None

        
    def get_screenshot(self):
        # Re-find the window handle on each call to ensure we're capturing the current window
        # This prevents issues with stale handles or window state caching
        current_hwnd = win32gui.FindWindow(None, self.window_name)
        if not current_hwnd:
            raise Exception(f"ERROR: Window '{self.window_name}' not found. Window may have been closed.")
        
        # Use the current handle instead of the cached one
        self.hwnd = current_hwnd
        
        # Verify window is still valid
        if not win32gui.IsWindow(self.hwnd):
            raise Exception(f"ERROR: Window '{self.window_name}' no longer exists. Please restart the application.")
        
        # Re-verify window dimensions in case window was resized
        window_rect = win32gui.GetWindowRect(self.hwnd)
        if not window_rect or len(window_rect) < 4:
            raise Exception(f"ERROR: Failed to get window dimensions for '{self.window_name}'. Window may be invalid.")
        
        current_w = window_rect[2] - window_rect[0]
        current_h = window_rect[3] - window_rect[1]
        
        if current_w <= 0 or current_h <= 0:
            raise Exception(f"ERROR: Invalid window dimensions ({current_w}x{current_h}) for '{self.window_name}'. Window may be minimized.")
        
        # Update dimensions if window was resized
        if current_w != self.w or current_h != self.h:
            self.w = current_w
            self.h = current_h
        
        # Try mss first (Desktop Duplication API - best for Windows 10+, works like komari's "Windows 10 mode")
        # This is more reliable than BitBlt for game windows (DirectX/Direct3D)
        if MSS_AVAILABLE and self.sct is not None:
            try:
                # Use the window_rect we already got above
                left = window_rect[0]
                top = window_rect[1]
                
                # Capture using mss (Desktop Duplication API)
                monitor = {
                    "left": left,
                    "top": top,
                    "width": self.w,
                    "height": self.h
                }
                
                # Grab the screenshot
                sct_img = self.sct.grab(monitor)
                
                # Convert to numpy array (BGRA format)
                img = np.array(sct_img)
                
                # Convert BGRA to BGR for OpenCV
                img_bgr = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
                
                return img_bgr
            except Exception as e:
                # If mss fails, fall back to other methods
                pass
        
        # Try PrintWindow (better for DirectX/Direct3D windows, forces fresh rendering)
        # PW_RENDERFULLCONTENT = 0x00000002 - renders even if window is offscreen
        try:
            # Create a memory DC for PrintWindow
            hdcScreen = win32gui.GetDC(0)
            hdcMem = win32ui.CreateCompatibleDC(hdcScreen)
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdcScreen, self.w, self.h)
            hdcMem.SelectObject(hbmp)
            
            # Use PrintWindow to capture (this can capture DirectX content better)
            # PW_RENDERFULLCONTENT forces full content rendering even if window is offscreen
            PW_RENDERFULLCONTENT = 0x00000002
            result = win32gui.PrintWindow(self.hwnd, hdcMem.GetSafeHdc(), PW_RENDERFULLCONTENT)
            
            if result:
                # Get bitmap bits
                signedIntsArray = hbmp.GetBitmapBits(True)
                win32gui.ReleaseDC(0, hdcScreen)
                hdcMem.DeleteDC()
                win32gui.DeleteObject(hbmp.GetHandle())
                
                if signedIntsArray:
                    img = np.fromstring(signedIntsArray, dtype='uint8')
                    if img is not None and img.size > 0:
                        expected_size = self.h * self.w * 4
                        if img.size == expected_size:
                            img.shape = (self.h, self.w, 4)
                            img = np.ascontiguousarray(img)
                            img_bgr = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
                            return img_bgr
        except Exception as e:
            # If PrintWindow fails, fall back to BitBlt
            pass
        
        # Fallback to BitBlt method
        wDC = win32gui.GetWindowDC(self.hwnd)
        if not wDC:
            raise Exception(f"ERROR: Failed to get device context for window '{self.window_name}'.")
        
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        # Capture the entire window (no cropping)
        cDC.BitBlt((0,0),(self.w, self.h) , dcObj, (0,0), win32con.SRCCOPY)

        #save the screenshot for debugging
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        if not signedIntsArray:
            raise Exception(f"ERROR: Failed to get bitmap bits for window '{self.window_name}'. Bitmap may be empty.")
        
        img = np.fromstring(signedIntsArray, dtype='uint8')
        if img is None or img.size == 0:
            raise Exception(f"ERROR: Failed to create image array for window '{self.window_name}'. Array is empty.")
        
        expected_size = self.h * self.w * 4
        if img.size != expected_size:
            raise Exception(f"ERROR: Image size mismatch for window '{self.window_name}'. Expected {expected_size}, got {img.size}.")
        
        img.shape = (self.h,self.w,4 )

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        img = np.ascontiguousarray(img)
        
        # Convert BGRA to BGR (remove alpha channel) for OpenCV compatibility
        # OpenCV expects BGR format, not BGRA
        img_bgr = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
        
        return img_bgr
