import cv2 as cv
import numpy as np
from numpy import interp


def invert_image(image):
    return cv.bitwise_not(image)

def greyscale(image):
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

def adjust_threshold_fixed(gray_image, threshold=127):
    """Fixed threshold - works well for high contrast images"""
    thresh, img_bw = cv.threshold(gray_image, threshold, 255, cv.THRESH_BINARY)
    return img_bw

def adjust_threshold_adaptive(gray_image):
    """Adaptive threshold - works better for varying lighting conditions"""
    # Use adaptive thresholding which works better for different resolutions
    img_bw = cv.adaptiveThreshold(gray_image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv.THRESH_BINARY, 11, 2)
    return img_bw

def adjust_scale(image, scale_factor=None):
    """Scale image - adaptive scaling based on resolution"""
    if scale_factor is None:
        # Adaptive scaling: only scale if image is small
        h, w = image.shape[:2]
        # If image is already large (>1000px), don't scale or scale less
        if max(h, w) > 1000:
            # Scale down slightly for very large images, or don't scale
            if max(h, w) > 2000:
                scale_factor = 1.0  # Don't scale very large images
            else:
                scale_factor = 1.5  # Light scaling for medium-large images
        else:
            scale_factor = 3.0  # Original scaling for small images
    
    if scale_factor == 1.0:
        return image
    
    return cv.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv.INTER_CUBIC)

def enhance_contrast(image):
    """Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(image)

def image_process(image, method='adaptive'):
    """
    Process image for OCR with multiple methods.
    
    Args:
        image: Input image (BGR format from window capture)
        method: Processing method - 'adaptive', 'fixed', 'simple', or 'original'
    
    Returns:
        Processed grayscale image ready for OCR
    """
    # Convert BGR to grayscale first
    gray = greyscale(image)
    
    if method == 'simple':
        # Simplest method: just grayscale, no aggressive processing
        # Sometimes raw grayscale works better than processed
        return gray
    
    elif method == 'original':
        # Original method: invert, threshold, scale
        inverted = invert_image(gray)
        thresholded = adjust_threshold_fixed(inverted, 127)
        scaled = adjust_scale(thresholded)
        return scaled
    
    elif method == 'fixed':
        # Fixed threshold method
        inverted = invert_image(gray)
        thresholded = adjust_threshold_fixed(inverted, 127)
        scaled = adjust_scale(thresholded)
        return scaled
    
    elif method == 'adaptive':
        # Adaptive method - use enhanced contrast + adaptive threshold (most effective)
        # Optimized: only create the method that works best, not all 3
        enhanced = enhance_contrast(gray)
        adaptive = adjust_threshold_adaptive(enhanced)
        scaled = adjust_scale(adaptive)
        return scaled
    
    else:
        # Default: adaptive
        return image_process(image, 'adaptive')