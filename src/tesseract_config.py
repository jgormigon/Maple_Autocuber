"""
Tesseract OCR Configuration
Automatically detects and configures Tesseract path for bundled executable or system installation.
"""
import os
import sys
import pytesseract

_TESSERACT_EXE = None
_TESSDATA_DIR = None

def get_tesseract_exe():
    """Return detected tesseract executable path if configured."""
    return _TESSERACT_EXE

def get_tessdata_dir():
    """Return detected tessdata directory if available."""
    return _TESSDATA_DIR or os.environ.get("TESSDATA_PREFIX")

def wrap_tesseract_config(config: str) -> str:
    """
    Ensure Tesseract can find its traineddata in bundled builds.
    Prepends --tessdata-dir when we know the tessdata directory.
    """
    td = get_tessdata_dir()
    if td and config is not None and "--tessdata-dir" not in config:
        # IMPORTANT: Don't embed quotes here.
        # In PyInstaller builds, pytesseract/tesseract can end up receiving the quotes literally,
        # producing paths like:  "\"C:\\...\\tessdata\"/eng.traineddata" and failing to load eng.
        return f'--tessdata-dir {td} {config}'.strip()
    return config

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
            global _TESSERACT_EXE, _TESSDATA_DIR
            _TESSERACT_EXE = tesseract_exe
            pytesseract.pytesseract.tesseract_cmd = tesseract_exe
            print(f"[TESSERACT] Using bundled Tesseract: {tesseract_exe}")
            # Ensure bundled tessdata is discoverable even if cwd changes (PyInstaller / GUI apps).
            candidate_tessdata = os.path.join(os.path.dirname(tesseract_exe), "tessdata")
            if os.path.isdir(candidate_tessdata):
                _TESSDATA_DIR = candidate_tessdata
                os.environ["TESSDATA_PREFIX"] = candidate_tessdata
                if os.path.exists(os.path.join(candidate_tessdata, "eng.traineddata")):
                    print(f"[TESSERACT] Using bundled tessdata: {candidate_tessdata}")
                else:
                    print(f"[TESSERACT] Warning: tessdata folder found but eng.traineddata missing: {candidate_tessdata}")
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

