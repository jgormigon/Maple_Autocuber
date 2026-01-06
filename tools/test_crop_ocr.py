"""
Test script to see what lines OCR reads from the crop region
"""
import cv2 as cv
import sys
import os
from auto_detect_crop import detect_potential_region
from translate_ocr_results import get_lines, split_lines, process_lines
from crop_config import OFFSET_X, OFFSET_ABOVE
import pytesseract

def test_crop_ocr(image_path, debug=True):
    """
    Test what OCR reads from the auto-detected crop region
    
    Args:
        image_path: Path to test image
        debug: If True, show detailed output and save debug images
    """
    print(f"\n{'='*60}")
    print(f"Testing OCR on crop region")
    print(f"Image: {image_path}")
    print(f"{'='*60}\n")
    
    # Load image
    img = cv.imread(image_path)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return
    
    h, w = img.shape[:2]
    print(f"Image dimensions: {w}x{h}\n")
    
    # Auto-detect crop region
    print("Step 1: Auto-detecting crop region...")
    result = detect_potential_region(img, debug=debug)
    
    if result is None:
        print("ERROR: Could not detect crop region!")
        return
    
    # detect_potential_region returns ((crop_x, crop_y, crop_w, crop_h), (reset_x, reset_y, reset_w, reset_h) or None)
    crop_region, reset_button = result
    if crop_region is None:
        print("ERROR: Could not detect crop region!")
        return
    
    crop_x, crop_y, crop_w, crop_h = crop_region
    print(f"Detected crop region: x={crop_x}, y={crop_y}, w={crop_w}, h={crop_h}\n")
    
    # Validate crop region before cropping
    if crop_w <= 0 or crop_h <= 0:
        print(f"ERROR: Invalid crop region dimensions! w={crop_w}, h={crop_h}")
        print(f"  This usually means the offsets in crop_config.py need adjustment.")
        print(f"  Current offsets: OFFSET_X={OFFSET_X}, OFFSET_ABOVE={OFFSET_ABOVE}")
        print(f"  Image size: {w}x{h}")
        print(f"  Crop region: x={crop_x}, y={crop_y}, w={crop_w}, h={crop_h}")
        return
    
    # Crop the image
    try:
        cropped_img = img[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
        if cropped_img is None or cropped_img.size == 0:
            print("ERROR: Failed to crop image!")
            return
    except Exception as e:
        print(f"ERROR: Failed to crop image: {e}")
        print(f"  Crop region: x={crop_x}, y={crop_y}, w={crop_w}, h={crop_h}")
        print(f"  Image size: {w}x{h}")
        return
    
    # Save cropped image for inspection
    cv.imwrite('test_cropped_region.png', cropped_img)
    print(f"Saved cropped region to: test_cropped_region.png")
    
    # Also save visualization with crop region marked on original image
    vis_img = img.copy()
    cv.rectangle(vis_img, (crop_x, crop_y), (crop_x + crop_w, crop_y + crop_h), (0, 255, 0), 2)
    cv.putText(vis_img, "Crop Region", (crop_x, crop_y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv.imwrite('test_crop_visualization.png', vis_img)
    print(f"Saved visualization to: test_crop_visualization.png\n")
    
    # Test OCR using the same method as the bot
    print("Step 2: Running OCR on cropped region...")
    print("-" * 60)
    
    # Test with auto-detect enabled (bot's normal mode)
    print("\n2a. Testing with auto_detect_crop=True (bot's normal mode):")
    raw_ocr_text_auto = get_lines(
        window_name=None,
        debug=debug,
        crop_region=None,  # Will be auto-detected
        test_image_path=image_path,
        auto_detect_crop=True
    )
    
    print(f"Raw OCR Text (auto-detect):")
    if raw_ocr_text_auto:
        print(f"  {repr(raw_ocr_text_auto)}")
    else:
        print("  (Empty or None)")
    
    # Also test with manual crop region
    print("\n2b. Testing with manual crop region:")
    raw_ocr_text = get_lines(
        window_name=None,
        debug=debug,
        crop_region=crop_region,
        test_image_path=image_path,
        auto_detect_crop=False  # Use provided crop region
    )
    
    # Use the auto-detected result if manual is empty
    if not raw_ocr_text and raw_ocr_text_auto:
        raw_ocr_text = raw_ocr_text_auto
        print("  (Using auto-detected result)")
    
    print(f"\nRaw OCR Text:")
    print(f"{'='*60}")
    if raw_ocr_text:
        print(repr(raw_ocr_text))
        print(f"\nFormatted:")
        print(raw_ocr_text)
    else:
        print("(Empty or None)")
    print(f"{'='*60}\n")
    
    # Split into lines
    print("Step 3: Splitting into lines...")
    print("-" * 60)
    lines = split_lines(raw_ocr_text)
    print(f"Found {len(lines)} lines:")
    for i, line in enumerate(lines, 1):
        print(f"  {i}. {repr(line)}")
    print()
    
    # Process lines (what the bot actually uses)
    print("Step 4: Processing lines (bot logic)...")
    print("-" * 60)
    result = process_lines(
        window_name=None,
        debug=debug,
        crop_region=crop_region,
        test_image_path=image_path,
        auto_detect_crop=False
    )
    
    line1, line2, line3 = result if len(result) >= 3 else (result[0], result[1], "Trash")
    print(f"\nBot Result:")
    print(f"  Line 1: {line1}")
    print(f"  Line 2: {line2}")
    if line3 and line3 != "Trash":
        print(f"  Line 3: {line3}")
    
    # Calculate and show total stats
    from translate_ocr_results import get_stat_from_line
    stats = {"STR": 0, "DEX": 0, "INT": 0, "LUK": 0, "ALL": 0, "ATT": 0}
    for line in [line1, line2, line3]:
        if line and line != "Trash":
            stat_type, stat_value = get_stat_from_line(line)
            if stat_type:
                if stat_type == "ALL":
                    stats["ALL"] += stat_value
                elif stat_type == "ATT":
                    stats["ATT"] += stat_value
                else:
                    stats[stat_type] += stat_value
    
    # Apply ALL stats to main stats
    if stats["ALL"] > 0:
        stats["STR"] += stats["ALL"]
        stats["DEX"] += stats["ALL"]
        stats["INT"] += stats["ALL"]
        stats["LUK"] += stats["ALL"]
    
    stat_parts = []
    for stat_type in ["STR", "DEX", "INT", "LUK", "ATT"]:
        if stats.get(stat_type, 0) > 0:
            stat_parts.append(f"{stat_type}: {stats[stat_type]}")
    if stats.get("ALL", 0) > 0:
        stat_parts.append(f"ALL: {stats['ALL']}")
    
    if stat_parts:
        print(f"  Total Stats: {', '.join(stat_parts)}")
    print()
    
    # Also try direct OCR on cropped image for comparison
    print("Step 5: Direct OCR test (for comparison)...")
    print("-" * 60)
    
    # Try different OCR methods
    gray = cv.cvtColor(cropped_img, cv.COLOR_BGR2GRAY)
    
    ocr_configs = [
        ('--psm 6', 'uniform block'),
        ('--psm 11', 'sparse text'),
        ('--psm 7', 'single line'),
        ('--psm 12', 'sparse text with OSD'),
    ]
    
    for psm_config, psm_desc in ocr_configs:
        try:
            result = pytesseract.image_to_string(gray, config=psm_config)
            if result and result.strip():
                print(f"\nPSM {psm_config} ({psm_desc}):")
                print(f"  {repr(result[:200])}")
        except Exception as e:
            print(f"Error with {psm_config}: {e}")
    
    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_crop_ocr.py <image_path> [--debug]")
        print("\nExample:")
        print("  python test_crop_ocr.py test.png")
        print("  python test_crop_ocr.py test.png --debug")
        return
    
    image_path = sys.argv[1]
    debug = '--debug' in sys.argv or '-d' in sys.argv
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return
    
    test_crop_ocr(image_path, debug=debug)


if __name__ == "__main__":
    main()

