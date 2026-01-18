"""
Tool to find the optimal crop region for the Potential lines section
"""
import cv2 as cv
import numpy as np
import pytesseract
from src.crop_config import OFFSET_X, OFFSET_ABOVE, STAT_WIDTH, STAT_HEIGHT
from PIL import Image
from src.auto_detect_crop import detect_potential_region as auto_detect

def find_potential_region(image_path, debug=True):
    """
    Find the region containing the Potential lines by looking for "Reset" button as an anchor
    and then calculating the crop region relative to it.
    
    Returns: (x, y, width, height) in pixels
    """
    # Load image
    img = cv.imread(image_path)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return None
    
    h, w = img.shape[:2]
    print(f"Image size: {w}x{h}")
    
    # Use the same detection function as auto_detect_crop.py for consistency
    print("\nUsing auto_detect_crop.detect_potential_region() for consistency...")
    result = auto_detect(img, debug=debug)
    
    if result:
        # detect_potential_region returns ((crop_x, crop_y, crop_w, crop_h), (reset_x, reset_y, reset_w, reset_h) or None)
        crop_region, reset_pos = result
        crop_x, crop_y, crop_w, crop_h = crop_region
        print(f"\n{'='*60}")
        print(f"CROP REGION DETECTED:")
        print(f"{'='*60}")
        print(f"Pixel coordinates: ({crop_x}, {crop_y}, {crop_w}, {crop_h})")
        print(f"\nPercentages (for GUI):")
        print(f"  X: {crop_x/w:.4f}")
        print(f"  Y: {crop_y/h:.4f}")
        print(f"  Width: {crop_w/w:.4f}")
        print(f"  Height: {crop_h/h:.4f}")
        
        # Save visualization
        vis_img = img.copy()
        # Try to find Reset button for visualization
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        enhanced_gray = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
        try:
            ocr_data = pytesseract.image_to_data(enhanced_gray, output_type=pytesseract.Output.DICT, config='--psm 6')
            for i, text in enumerate(ocr_data['text']):
                text_lower = text.lower().strip()
                if 'reset' in text_lower:
                    reset_x = ocr_data['left'][i]
                    reset_y = ocr_data['top'][i]
                    reset_w = ocr_data['width'][i]
                    reset_h = ocr_data['height'][i]
                    cv.rectangle(vis_img, (reset_x, reset_y), (reset_x + reset_w, reset_y + reset_h), (255, 0, 0), 2)
                    cv.putText(vis_img, "Reset (Anchor)", (reset_x, reset_y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    break
        except:
            pass
        
        cv.rectangle(vis_img, (crop_x, crop_y), (crop_x + crop_w, crop_y + crop_h), (0, 255, 0), 2)
        cv.putText(vis_img, "Detected Potential Region", (crop_x, crop_y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv.imwrite('crop_region_visualization.png', vis_img)
        print(f"\nSaved visualization to: crop_region_visualization.png")
        
        # Crop and save the region
        try:
            cropped = img[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
            if cropped is not None and cropped.size > 0:
                cv.imwrite('detected_potential_region.png', cropped)
                print(f"Saved cropped region to: detected_potential_region.png")
        except Exception as e:
            print(f"Error cropping image: {e}")
        
        return crop_region
    
    print("\nCould not detect crop region automatically.")
    print("Falling back to manual detection method...")
    print("="*60)
    
    # Fallback to original method if auto_detect fails
    # Convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Enhance contrast for better OCR
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_gray = clahe.apply(gray)
    
    # Try multiple OCR configurations
    ocr_configs = [
        ('--psm 6', 'uniform block'),
        ('--psm 11', 'sparse text'),
        ('--psm 7', 'single line'),
        ('--psm 8', 'single word'),
        ('--psm 12', 'sparse text with OSD'),
    ]
    
    images_to_try = [
        (gray, 'original'),
        (enhanced_gray, 'enhanced'),
    ]
    
    # Find "Reset" button text as anchor
    reset_y = None
    reset_x = None
    reset_w = None
    reset_h = None
    all_matches = []
    
    try:
        for img_ocr, img_name in images_to_try:
            for psm_config, psm_desc in ocr_configs:
                try:
                    # Get OCR data with bounding boxes
                    ocr_data = pytesseract.image_to_data(img_ocr, output_type=pytesseract.Output.DICT, config=psm_config)
                    
                    # Search for "Reset" button text
                    for i, text in enumerate(ocr_data['text']):
                        text_lower = text.lower().strip()
                        if len(text_lower) > 0:
                            # Check for "reset" - should be exact or close match
                            if text_lower == 'reset' or 'reset' in text_lower:
                                x = ocr_data['left'][i]
                                y = ocr_data['top'][i]
                                width = ocr_data['width'][i]
                                height = ocr_data['height'][i]
                                conf = ocr_data['conf'][i]
                                
                                if conf >= -1:  # Accept even low confidence
                                    all_matches.append((x, y, width, height, conf, text, psm_config, img_name))
                                    print(f"Found 'Reset' match: '{text}' at x={x}, y={y}, w={width}, h={height}, conf={conf}, psm={psm_config}, img={img_name}")
                except Exception as e:
                    if debug:
                        print(f"Error with PSM {psm_config}: {e}")
                    continue
        
        # Remove duplicates and select best match
        if all_matches:
            # Remove duplicates (same location)
            unique_matches = []
            seen = set()
            for match in all_matches:
                x, y, w, h, conf, text, psm, img_name = match
                loc_key = (x // 20, y // 20)  # Group by 20px grid
                if loc_key not in seen:
                    seen.add(loc_key)
                    unique_matches.append(match)
            
            # Sort by confidence (prefer higher confidence)
            unique_matches.sort(key=lambda m: -m[4])  # -conf for descending
            
            reset_x, reset_y, reset_w, reset_h, conf, text, psm, img_name = unique_matches[0]
            print(f"\nSelected best 'Reset' match:")
            print(f"  Text: '{text}'")
            print(f"  Position: x={reset_x}, y={reset_y}, w={reset_w}, h={reset_h}")
            print(f"  Confidence: {conf}")
            print(f"  PSM: {psm}, Image: {img_name}")
            if len(unique_matches) > 1:
                print(f"  (Found {len(unique_matches)} unique matches, selected highest confidence)")
        
        if reset_y is None:
            print("\nCould not find 'Reset' text. Showing what OCR found:")
            # Show all OCR results for debugging
            try:
                ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config='--psm 6')
                all_texts = [(ocr_data['text'][i], ocr_data['left'][i], ocr_data['top'][i], ocr_data['conf'][i]) 
                            for i in range(len(ocr_data['text'])) if len(ocr_data['text'][i].strip()) > 0]
                print("OCR found these texts (first 20):")
                for text, x, y, conf in all_texts[:20]:
                    print(f"  '{text}' at ({x}, {y}), conf={conf}")
            except:
                pass
        
        
        if reset_y is not None:
            # Found Reset button anchor, now estimate the region for the Potential stat lines
            # The stat lines (including "Attack Power +xx") are typically above the Reset button
            # The Reset button is usually at the bottom of the Potential window
            
            print(f"\nReset button found at: x={reset_x}, y={reset_y}, w={reset_w}, h={reset_h}")
            print(f"Image dimensions: {w}x{h}")
            
            # Load offsets from config file
            # These offsets are relative to the Reset button position
            # See crop_config.py to adjust these values
            
            # Calculate crop region based on Reset button position
            # X position: Reset X + OFFSET_X
            # If OFFSET_X is negative, crop goes LEFT of Reset
            # If OFFSET_X is positive, crop goes RIGHT of Reset
            initial_crop_x = reset_x + OFFSET_X
            crop_x = max(0, initial_crop_x)
            # Y position: Reset Y - OFFSET_ABOVE (moves up from Reset button)
            initial_crop_y = reset_y - OFFSET_ABOVE
            crop_y = max(0, initial_crop_y)
            # Width: enough for stat lines (should be narrow, only covering right panel stat area)
            crop_w = min(w - crop_x, STAT_WIDTH)
            # Height: use fixed height from config
            crop_h = min(STAT_HEIGHT, h - crop_y)
            
            print(f"Crop calculation (initial):")
            print(f"  Reset button: x={reset_x}, y={reset_y}, w={reset_w}, h={reset_h}")
            print(f"  Config values: OFFSET_X={OFFSET_X}, OFFSET_ABOVE={OFFSET_ABOVE}, STAT_WIDTH={STAT_WIDTH}, STAT_HEIGHT={STAT_HEIGHT}")
            print(f"  Initial crop_x = {reset_x} + {OFFSET_X} = {initial_crop_x} -> clamped to {crop_x}")
            print(f"  Initial crop_y = {reset_y} - {OFFSET_ABOVE} = {initial_crop_y} -> clamped to {crop_y}")
            print(f"  Initial crop_w = min({w} - {crop_x}, {STAT_WIDTH}) = {crop_w}")
            print(f"  Initial crop_h = min({STAT_HEIGHT}, {h} - {crop_y}) = {crop_h}")
            
            # Validate and fix crop region to ensure positive dimensions
            if crop_w <= 0:
                print(f"Warning: Calculated width is negative or zero ({crop_w}), adjusting...")
                # If crop_x is too far right, move it left
                crop_x = max(0, w - STAT_WIDTH)
                crop_w = min(STAT_WIDTH, w - crop_x)
                print(f"  Adjusted: crop_x={crop_x}, crop_w={crop_w}")
            
            if crop_h <= 0:
                print(f"Warning: Calculated height is negative or zero ({crop_h}), adjusting...")
                # If crop_y is too far down, move it up
                crop_y = max(0, h - STAT_HEIGHT)
                crop_h = min(STAT_HEIGHT, h - crop_y)
                print(f"  Adjusted: crop_y={crop_y}, crop_h={crop_h}")
            
            # Final validation - ensure all values are positive and within bounds
            final_crop_x = max(0, min(crop_x, w - 1))
            final_crop_y = max(0, min(crop_y, h - 1))
            final_crop_w = max(1, min(crop_w, w - crop_x))
            final_crop_h = max(1, min(crop_h, h - crop_y))
            
            # Only update if changed
            if final_crop_x != crop_x or final_crop_y != crop_y or final_crop_w != crop_w or final_crop_h != crop_h:
                print(f"Final bounds check adjustments:")
                print(f"  crop_x: {crop_x} -> {final_crop_x}")
                print(f"  crop_y: {crop_y} -> {final_crop_y}")
                print(f"  crop_w: {crop_w} -> {final_crop_w}")
                print(f"  crop_h: {crop_h} -> {final_crop_h}")
            
            crop_x, crop_y, crop_w, crop_h = final_crop_x, final_crop_y, final_crop_w, final_crop_h
            
            print(f"\nFinal crop region:")
            print(f"  X: {crop_x} ({crop_x/w:.2%} of width)")
            print(f"  Y: {crop_y} ({crop_y/h:.2%} of height)")
            print(f"  Width: {crop_w} ({crop_w/w:.2%} of width)")
            print(f"  Height: {crop_h} ({crop_h/h:.2%} of height)")
            print(f"  Region: ({crop_x}, {crop_y}) to ({crop_x + crop_w}, {crop_y + crop_h})")
            
            print(f"\nSuggested crop region:")
            print(f"  X: {crop_x} ({crop_x/w:.2%} of width) - Reset X: {reset_x}, Offset: {OFFSET_X} (negative=left, positive=right)")
            print(f"  Y: {crop_y} ({crop_y/h:.2%} of height) - Reset Y: {reset_y}, Offset: -{OFFSET_ABOVE} (above Reset)")
            print(f"  Width: {crop_w} ({crop_w/w:.2%} of width)")
            print(f"  Height: {crop_h} ({crop_h/h:.2%} of height) - Fixed height: {STAT_HEIGHT}px")
            print(f"\nTo adjust, modify OFFSET_X, OFFSET_ABOVE, STAT_WIDTH, or STAT_HEIGHT in the code")
            print(f"  - OFFSET_X: negative = left of Reset, positive = right of Reset")
            print(f"  - OFFSET_ABOVE: pixels above Reset button")
            print(f"  - STAT_WIDTH: width of crop region")
            print(f"  - STAT_HEIGHT: fixed height of crop region")
            
            # Save visualization (using already validated crop region)
            vis_img = img.copy()
            # Draw box around Reset button (anchor)
            cv.rectangle(vis_img, (reset_x, reset_y), 
                       (reset_x + reset_w, reset_y + reset_h), (255, 0, 0), 2)
            cv.putText(vis_img, "Reset (Anchor)", (reset_x, reset_y - 10), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            # Draw box around detected Potential region
            cv.rectangle(vis_img, (crop_x, crop_y), (crop_x + crop_w, crop_y + crop_h), (0, 255, 0), 2)
            cv.putText(vis_img, "Detected Potential Region", (crop_x, crop_y - 10), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv.imwrite('crop_region_visualization.png', vis_img)
            print(f"\nSaved visualization to: crop_region_visualization.png")
            
            print(f"Final crop region: x={crop_x}, y={crop_y}, w={crop_w}, h={crop_h}")
            
            # Crop and save the region
            try:
                cropped = img[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
                if cropped is not None and cropped.size > 0:
                    cv.imwrite('detected_potential_region.png', cropped)
                    print(f"Saved cropped region to: detected_potential_region.png")
                else:
                    print(f"Warning: Cropped image is empty. Crop region: x={crop_x}, y={crop_y}, w={crop_w}, h={crop_h}")
            except Exception as e:
                print(f"Error cropping image: {e}")
                print(f"Crop region: x={crop_x}, y={crop_y}, w={crop_w}, h={crop_h}, image size={w}x{h}")
            
            return (crop_x, crop_y, crop_w, crop_h)
        else:
            print("Could not detect Potential region automatically.")
            print("Please manually inspect the image and provide coordinates.")
            return None
            
    except Exception as e:
        print(f"Error during OCR detection: {e}")
        import traceback
        traceback.print_exc()
        return None

def manual_crop_from_image(image_path, x, y, w, h):
    """Manually crop an image given coordinates"""
    img = cv.imread(image_path)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return None
    
    h_img, w_img = img.shape[:2]
    
    # Ensure coordinates are within bounds
    x = max(0, min(x, w_img - 1))
    y = max(0, min(y, h_img - 1))
    w = min(w, w_img - x)
    h = min(h, h_img - y)
    
    cropped = img[y:y+h, x:x+w]
    return cropped

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python find_crop_region.py <image_path>")
        print("Example: python find_crop_region.py test_image.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = find_potential_region(image_path, debug=True)
    
    if result:
        x, y, w, h = result
        # Load image again to get dimensions for percentage calculation
        img = cv.imread(image_path)
        if img is not None:
            img_h, img_w = img.shape[:2]
            print(f"\n{'='*60}")
            print(f"CROP REGION FOUND:")
            print(f"{'='*60}")
            print(f"Pixel coordinates: ({x}, {y}, {w}, {h})")
            print(f"\nFor GUI (percentages):")
            print(f"  X: {x/img_w:.4f}")
            print(f"  Y: {y/img_h:.4f}")
            print(f"  Width: {w/img_w:.4f}")
            print(f"  Height: {h/img_h:.4f}")
        else:
            print(f"\n{'='*60}")
            print(f"CROP REGION FOUND:")
            print(f"{'='*60}")
            print(f"Pixel coordinates: ({x}, {y}, {w}, {h})")
    else:
        print("\nCould not automatically detect crop region.")
        print("Please check the visualization image and adjust manually.")

