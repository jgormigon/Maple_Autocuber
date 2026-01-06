"""
Tesseract OCR Configuration
Automatically detects and configures Tesseract path for bundled executable or system installation.
"""
import os
import sys
import pytesseract

def configure_tesseract():
    """
    Configure pytesseract to use bundled Tesseract if available, otherwise use system Tesseract.
    This should be called before any pytesseract usage.
    """
    # Check if we're running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check for bundled Tesseract in the executable directory
    # When PyInstaller extracts files, tesseract folder will be in the temp directory
    bundled_tesseract_paths = [
        # In PyInstaller temp directory (sys._MEIPASS)
        os.path.join(base_path, 'tesseract', 'tesseract.exe'),
        # In executable directory (for portable builds)
        os.path.join(os.path.dirname(sys.executable), 'tesseract', 'tesseract.exe'),
        # In current working directory
        os.path.join(os.getcwd(), 'tesseract', 'tesseract.exe'),
    ]
    
    # Also check project root for development (when running as script)
    if not getattr(sys, 'frozen', False):
        # Check in project root (parent of this file's directory)
        project_root = os.path.dirname(base_path)
        project_tesseract = os.path.join(project_root, 'tesseract', 'tesseract.exe')
        bundled_tesseract_paths.insert(0, project_tesseract)
    
    # Try to find bundled Tesseract
    for tesseract_exe in bundled_tesseract_paths:
        if os.path.exists(tesseract_exe):
            pytesseract.pytesseract.tesseract_cmd = tesseract_exe
            print(f"[TESSERACT] Using bundled Tesseract: {tesseract_exe}")
            return True
    
    # If bundled not found, try to use system Tesseract
    # pytesseract will try to find it in PATH automatically
    try:
        # Test if system Tesseract is available
        pytesseract.get_tesseract_version()
        print("[TESSERACT] Using system Tesseract (from PATH)")
        return True
    except Exception as e:
        print(f"[TESSERACT] Warning: Could not find Tesseract. Error: {e}")
        print("[TESSERACT] Please ensure Tesseract OCR is installed or bundled with the executable.")
        return False

# Auto-configure on import
configure_tesseract()

