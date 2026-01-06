# Quick Start: Building the Executable

## Prerequisites

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Ensure Tesseract is bundled:
   - Portable Tesseract should be in `tesseract/` folder at project root
   - The build will automatically include it in the executable

## Build Steps

### Windows
Double-click `build.bat` or run:
```bash
build.bat
```

### Linux/Mac
```bash
chmod +x build.sh
./build.sh
```

## Output

The executable will be in `dist/MapleAutocuber.exe` (Windows) or `dist/MapleAutocuber` (Linux/Mac)

## Important Notes

- Tesseract OCR is bundled with the executable - no separate installation needed!
- The executable includes all dependencies and assets (templates folder, config file, Tesseract)
- File size will be large (100-200MB+) - this is normal due to bundled Tesseract
- For debugging, change `console=False` to `console=True` in `build_exe.spec`

## Distribution

When sharing the executable:
1. Share the `.exe` file from the `dist` folder
2. No additional installation required - Tesseract is bundled!
3. Optionally include `crop_config.py` for customization

