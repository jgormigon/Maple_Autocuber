# Quick Start: Building the Executable

## Prerequisites

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location

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

- The executable requires Tesseract OCR to be installed on the target machine
- The executable includes all dependencies and assets (templates folder, config file)
- File size will be large (50-100MB+) - this is normal
- For debugging, change `console=False` to `console=True` in `build_exe.spec`

## Distribution

When sharing the executable:
1. Share the `.exe` file from the `dist` folder
2. Include instructions to install Tesseract OCR
3. Optionally include `crop_config.py` for customization

