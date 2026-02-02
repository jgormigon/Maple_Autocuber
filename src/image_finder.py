from concurrent.futures import process
import cv2 as cv
import numpy as np
import os
import sys
import time
from src.windowcapture import WindowCapture
from src.image_processing import image_process
import src.tesseract_config as tesseract_config  # Configure Tesseract path before importing pytesseract
import pytesseract
from PIL import Image
from src.auto_detect_crop import detect_potential_region

# Avoid changing CWD in frozen/PyInstaller builds: the module path may not exist on disk.
# In dev runs we keep the historical behavior (relative paths), but guard against failures.
if not getattr(sys, "frozen", False):
    try:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.isdir(module_dir):
            os.chdir(module_dir)
    except Exception:
        pass
# Default window name - can be overridden when creating potlines instance
DEFAULT_WINDOW_NAME = "Maplestory"

class potlines:
    image = None
    wincap = None
    crop_region = None  # (x, y, width, height) as percentages or pixels
    reset_button_pos = None  # (x, y, width, height) of Reset button in window coordinates
    test_image_path = None  # Path to test image file (for debugging)
    auto_detect_crop = False  # If True, automatically detect crop region
    last_screenshot = None  # Store last screenshot for saving when bot stops
    
    def __init__(self, window_name=None, crop_region=None, test_image_path=None, auto_detect_crop=False, cube_type="Glowing"):
        """
        Initialize potlines with optional window name and crop region.
        If window_name is not provided, uses DEFAULT_WINDOW_NAME.
        
        Args:
            window_name: Name of the window to capture (ignored if test_image_path is provided)
            crop_region: Tuple of (x, y, width, height) as percentages (0.0-1.0) or pixels
                        If percentages, will be relative to window size
                        Example: (0.3, 0.4, 0.4, 0.3) = 30% from left, 40% from top, 40% width, 30% height
            test_image_path: Path to a test image file (for debugging). If provided, uses this instead of window capture.
            cube_type: "Glowing" or "Bright" - determines which offsets to use for crop region calculation
        """
        self.crop_region = crop_region
        self.test_image_path = test_image_path
        self.auto_detect_crop = auto_detect_crop
        self.cube_type = cube_type
        # Clear any cached data
        self.image = None
        self.last_screenshot = None
        
        # If test image is provided, skip window capture
        if test_image_path:
            if not os.path.exists(test_image_path):
                raise Exception(f"Test image file not found: {test_image_path}")
            self.wincap = None
            print(f"[TEST MODE] Using test image: {test_image_path}")
        else:
            if window_name is None:
                window_name = DEFAULT_WINDOW_NAME
            
            # Initialize window capture with error handling
            try:
                self.wincap = WindowCapture(window_name)
            except Exception as e:
                error_msg = (
                    f"\n{'='*60}\n"
                    f"ERROR: Failed to initialize window capture!\n\n"
                    f"{str(e)}\n"
                    f"{'='*60}\n"
                )
                raise Exception(error_msg) from e
        
        # Don't take screenshot in __init__ - we take fresh screenshots in get_ocr_result()
        # This prevents caching issues
    
    def crop_image(self, image, debug=False):
        """Crop image to specified region"""
        if self.crop_region is None:
            return image
        
        h, w = image.shape[:2]
        x, y, crop_w, crop_h = self.crop_region
        
        # If values are <= 1.0, treat as percentages
        if x <= 1.0 and y <= 1.0 and crop_w <= 1.0 and crop_h <= 1.0:
            x_px = int(x * w)
            y_px = int(y * h)
            crop_w_px = int(crop_w * w)
            crop_h_px = int(crop_h * h)
        else:
            # Treat as pixels
            x_px = int(x)
            y_px = int(y)
            crop_w_px = int(crop_w)
            crop_h_px = int(crop_h)
        
        # Ensure crop region is within image bounds
        x_px = max(0, min(x_px, w - 1))
        y_px = max(0, min(y_px, h - 1))
        crop_w_px = max(1, min(crop_w_px, w - x_px))
        crop_h_px = max(1, min(crop_h_px, h - y_px))
        
        if debug:
            print(f"[DEBUG] Cropping image: region=({x_px}, {y_px}, {crop_w_px}, {crop_h_px}) from ({w}, {h})")
        
        cropped = image[y_px:y_px+crop_h_px, x_px:x_px+crop_w_px]
        return cropped

    def screenshot(self, debug=False, processing_method='adaptive'):
        try:
            # Clear cached image before taking new screenshot
            self.image = None
            
            # Use test image if provided, otherwise capture from window
            if self.test_image_path:
                screenshot = cv.imread(self.test_image_path)
                if screenshot is None:
                    raise Exception(f"Failed to load test image: {self.test_image_path}")
                if debug:
                    print(f"[TEST MODE] Loaded test image, shape: {screenshot.shape}")
            else:
                # Always take fresh screenshot - clear cache first
                self.last_screenshot = None
                screenshot = self.wincap.get_screenshot()
                if debug:
                    print(f"[DEBUG] Screenshot captured, shape: {screenshot.shape if screenshot is not None else 'None'}")
            
            # Auto-detect crop region if enabled and not already set
            # (cached after first detection to avoid re-detecting on every call)
            if self.auto_detect_crop and self.crop_region is None:
                if debug:
                    print(f"[DEBUG] Auto-detecting crop region from screenshot...")
                detected_region = detect_potential_region(screenshot, debug=debug)
                if detected_region:
                    self.crop_region = detected_region
                    if debug:
                        print(f"[DEBUG] Auto-detected crop region: {self.crop_region}")
                else:
                    if debug:
                        print(f"[DEBUG] Warning: Could not auto-detect crop region, using full image")
            
            if debug:
                print(f"[DEBUG] screenshot() - Crop region status: auto_detect_crop={self.auto_detect_crop}, crop_region={self.crop_region}")
            
            # Crop to region of interest if specified
            if self.crop_region:
                screenshot = self.crop_image(screenshot, debug=debug)
                if debug:
                    print(f"[DEBUG] After cropping, shape: {screenshot.shape}")
            
            # Try multiple processing methods if adaptive doesn't work
            processed_img = image_process(screenshot, method=processing_method)
            if debug:
                print(f"[DEBUG] Image processed with method '{processing_method}', shape: {processed_img.shape if processed_img is not None else 'None'}")
        except Exception as e:
            if debug:
                print(f"[DEBUG] Error in screenshot: {e}")
                import traceback
                traceback.print_exc()
            raise

        #cv.imshow('Potential lines', processed_img)
        self.image = processed_img
        #cv.waitKey(1)
    
    def save_debug_image(self):
        """Save the last screenshot to debug_original_image.png (called when bot stops)"""
        if self.last_screenshot is not None:
            try:
                save_screenshot = self.last_screenshot.copy()
                if save_screenshot.dtype != np.uint8:
                    save_screenshot = np.clip(save_screenshot, 0, 255).astype(np.uint8)
                cv.imwrite('debug_original_image.png', save_screenshot)
                print(f"Saved debug image to: debug_original_image.png (shape: {save_screenshot.shape})")
            except Exception as e:
                print(f"Error saving debug image: {e}")
        # Clear cached images after saving
        self.last_screenshot = None
        self.image = None
    
    def clear_cache(self):
        """Clear all cached images and data"""
        self.last_screenshot = None
        self.image = None
    
    def get_ocr_result(self, debug=False, processing_method='adaptive'):
        # Try multiple processing methods - start with simplest first
        # Order: simple (no processing) -> adaptive -> numbers (for better number recognition) -> fixed -> original
        methods_to_try = ['simple', 'adaptive', 'numbers', 'fixed', 'original']
        if processing_method and processing_method not in methods_to_try:
            methods_to_try.insert(0, processing_method)
        elif processing_method:
            # Move requested method to front
            if processing_method in methods_to_try:
                methods_to_try.remove(processing_method)
                methods_to_try.insert(0, processing_method)
        
        # Also try raw image (just cropped, no processing at all)
        last_result = ""
        
        # First, try raw cropped image without any processing
        try:
            if debug:
                print(f"[DEBUG] Trying raw cropped image (no processing)")
            
            # Get FRESH screenshot (from window or test image)
            # This ensures we always get the latest state, not a cached image
            # Clear any cached screenshot first
            self.last_screenshot = None
            if self.test_image_path:
                if debug:
                    print(f"[DEBUG] Using test image: {self.test_image_path}")
                raw_screenshot = cv.imread(self.test_image_path)
                if raw_screenshot is None:
                    raise Exception(f"Failed to load test image: {self.test_image_path}")
            else:
                # Always take a fresh screenshot - don't use cached image
                # No delay needed - screenshot is fast and window should be updated after click
                if debug:
                    print(f"[DEBUG] Taking fresh screenshot from window: {self.wincap.window_name if self.wincap else 'None'}")
                    print(f"[DEBUG] Window handle: {self.wincap.hwnd if self.wincap else 'None'}")
                raw_screenshot = self.wincap.get_screenshot()
                if debug:
                    print(f"[DEBUG] Screenshot captured successfully, shape: {raw_screenshot.shape if raw_screenshot is not None else 'None'}")
                    # Only save debug images in debug mode and only on first call (not every retry)
                    if debug and not hasattr(self, '_debug_image_saved'):
                        try:
                            cv.imwrite('debug_current_capture.png', raw_screenshot)
                            print(f"[DEBUG] Saved current screenshot to: debug_current_capture.png")
                            self._debug_image_saved = True
                        except Exception as e:
                            print(f"[DEBUG] Could not save debug screenshot: {e}")
            
            # Store screenshot for potential saving when bot stops (don't save during iterations)
            # Only store if we successfully got a screenshot
            if raw_screenshot is not None:
                self.last_screenshot = raw_screenshot.copy()
            
            # Auto-detect crop region if enabled and not already set
            # (This should already be set from __init__() or screenshot(), but check again just in case)
            if self.auto_detect_crop and self.crop_region is None:
                if debug:
                    print(f"[DEBUG] Auto-detecting crop region from raw screenshot...")
                result = detect_potential_region(raw_screenshot, debug=debug, cube_type=self.cube_type)
                if result:
                    # detect_potential_region returns ((crop_x, crop_y, crop_w, crop_h), (reset_x, reset_y, reset_w, reset_h) or None)
                    crop_region, reset_pos = result
                    self.crop_region = crop_region
                    self.reset_button_pos = reset_pos
                    if debug:
                        print(f"[DEBUG] Auto-detected crop region: {self.crop_region}")
                        if reset_pos:
                            print(f"[DEBUG] Auto-detected Reset button position: {reset_pos}")
                else:
                    if debug:
                        print(f"[DEBUG] Warning: Could not auto-detect crop region, using full image")
            
            if debug:
                print(f"[DEBUG] Crop region status: auto_detect_crop={self.auto_detect_crop}, crop_region={self.crop_region}")
                print(f"[DEBUG] Raw screenshot shape before cropping: {raw_screenshot.shape if raw_screenshot is not None else 'None'}")
            
            if self.crop_region:
                raw_screenshot = self.crop_image(raw_screenshot, debug=debug)
                if debug:
                    print(f"[DEBUG] Raw screenshot shape after cropping: {raw_screenshot.shape if raw_screenshot is not None else 'None'}")
                    # Only save debug images in debug mode and only on first call
                    if debug and not hasattr(self, '_debug_cropped_saved'):
                        try:
                            cv.imwrite('debug_current_cropped.png', raw_screenshot)
                            print(f"[DEBUG] Saved cropped screenshot to: debug_current_cropped.png")
                            self._debug_cropped_saved = True
                        except Exception as e:
                            print(f"[DEBUG] Could not save cropped debug screenshot: {e}")
            else:
                if debug:
                    print(f"[DEBUG] No crop region set - using full image")
            # Convert to grayscale only
            raw_gray = cv.cvtColor(raw_screenshot, cv.COLOR_BGR2GRAY)
            
            # Try OCR on raw image with multiple configs for better number recognition
            raw_result = ""
            raw_configs = [
                ('--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+%: ', 'raw with whitelist'),
                ('--psm 6', 'raw standard'),
                ('--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+%: ', 'raw single line'),
            ]
            for config, desc in raw_configs:
                try:
                    ocr_config = tesseract_config.wrap_tesseract_config(config)
                    test_result = pytesseract.image_to_string(raw_gray, config=ocr_config)
                    if test_result and len(test_result.strip()) > len(raw_result.strip()):
                        raw_result = test_result
                        if debug:
                            print(f"[DEBUG] Raw OCR with {desc}: {repr(test_result[:50])}")
                        if len(raw_result.strip()) > 2:
                            break
                except Exception as e:
                    try:
                        from src.translate_ocr_results import set_last_ocr_error
                        set_last_ocr_error(f"Tesseract OCR failed ({desc}): {e}")
                    except Exception:
                        pass
                    if debug:
                        print(f"[DEBUG] Error with {desc}: {e}")
                    continue
            if raw_result and len(raw_result.strip()) > 2:
                if debug:
                    print(f"[DEBUG] Success with raw image: {repr(raw_result[:100])}")
                return raw_result  # Early return - skip all processing methods
            elif raw_result:
                last_result = raw_result
        except Exception as e:
            if debug:
                print(f"[DEBUG] Error trying raw image: {e}")
        
        # Now try processed images
        for method in methods_to_try:
            try:
                self.screenshot(debug=debug, processing_method=method)
                if debug:
                    print(f"[DEBUG] Trying OCR with method: {method}")
                    print(f"[DEBUG] Image shape: {self.image.shape if self.image is not None else 'None'}")
                    print(f"[DEBUG] Image dtype: {self.image.dtype if self.image is not None else 'None'}")
                
                # Try OCR with optimized configuration (fewer PSM modes for speed)
                # PSM 6 works best for this use case (uniform block of text)
                # Add configs that prioritize number recognition
                psm_configs = [
                    ('--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+%: ', 'uniform block with whitelist'),  # Best for this use case with number focus
                    ('--psm 6', 'uniform block'),  # Best for this use case
                    ('--psm 11', 'sparse text'),   # Fallback if PSM 6 fails
                    ('--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+%: ', 'single line with whitelist'),  # Single line with number focus
                ]
                
                result = ""
                for psm_config, desc in psm_configs:
                    try:
                        ocr_config = tesseract_config.wrap_tesseract_config(psm_config)
                        test_result = pytesseract.image_to_string(self.image, config=ocr_config)
                        if test_result and len(test_result.strip()) > len(result.strip()):
                            result = test_result
                            if debug and result.strip():
                                print(f"[DEBUG] Best result so far from PSM {psm_config}: {repr(result[:50])}")
                            # Early exit if we get a good result
                            if result and len(result.strip()) > 2:
                                break
                    except Exception as e:
                        try:
                            from src.translate_ocr_results import set_last_ocr_error
                            set_last_ocr_error(f"Tesseract OCR failed ({desc}): {e}")
                        except Exception:
                            pass
                        continue
                
                # Check if result has meaningful content (more than just 1-2 characters)
                if result and len(result.strip()) > 2:
                    if debug:
                        print(f"[DEBUG] Success with method: {method}")
                        print(f"[DEBUG] OCR result length: {len(result)}")
                        print(f"[DEBUG] OCR result (first 100 chars): {repr(result[:100])}")
                    return result
                elif result and len(result.strip()) > 0:
                    # Keep track of partial results but continue trying
                    if len(result.strip()) > len(last_result.strip()):
                        last_result = result
                    if debug:
                        print(f"[DEBUG] Method {method} returned partial result: {repr(result)}")
                else:
                    if debug:
                        print(f"[DEBUG] Method {method} returned empty result")
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Error with method {method}: {e}")
                continue
        
        # If all methods failed, return last result (might be empty)
        if debug:
            print(f"[DEBUG] All processing methods failed, returning last result")
            print(f"[DEBUG] Final OCR result length: {len(last_result) if last_result else 0}")
        return last_result if last_result else ""

#pot=potlines()
#print(pot.get_ocr_result())
