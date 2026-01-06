# Building Maple Autocuber Executable

This guide explains how to build the Maple Autocuber bot into a standalone executable (.exe) file.

## Prerequisites

1. **Python 3.7+** installed
2. **All dependencies** from `requirements.txt` installed:
   ```bash
   pip install -r requirements.txt
   ```

3. **PyInstaller** (will be installed automatically by build script):
   ```bash
   pip install pyinstaller
   ```

4. **Tesseract OCR** installed on your system:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location (usually `C:\Program Files\Tesseract-OCR`)
   - The executable will need Tesseract to be installed on the target machine as well

## Building the Executable

### Windows
Simply run:
```bash
build.bat
```

Or manually:
```bash
pyinstaller build_exe.spec
```

### Linux/Mac
```bash
chmod +x build.sh
./build.sh
```

Or manually:
```bash
pyinstaller build_exe.spec
```

## Output

The executable will be created in the `dist` folder:
- **Windows**: `dist\MapleAutocuber.exe`
- **Linux/Mac**: `dist/MapleAutocuber`

## Important Notes

1. **Tesseract OCR**: The executable requires Tesseract OCR to be installed on the target machine. Make sure to include installation instructions for users.

2. **Templates Folder**: The `templates` folder (containing `reset_button.png.jpg`) is automatically included in the build.

3. **Configuration**: The `crop_config.py` file is included in the build. Users can modify it if needed.

4. **Console Mode**: By default, the executable runs without a console window. To enable console output for debugging, change `console=False` to `console=True` in `build_exe.spec`.

5. **File Size**: The executable will be large (50-100MB+) because it includes Python and all dependencies. This is normal.

## Distribution

When distributing the executable:
1. Include the executable file
2. Provide Tesseract OCR installation instructions
3. Include a README with usage instructions
4. Optionally include `crop_config.py` if users need to customize crop regions

## Troubleshooting

### "Tesseract not found" error
- Ensure Tesseract OCR is installed on the target machine
- Add Tesseract to system PATH, or modify the code to specify the Tesseract path

### Missing DLL errors
- Ensure all required Windows DLLs are available
- May need to install Visual C++ Redistributable

### Large file size
- This is normal - PyInstaller bundles Python and all dependencies
- Consider using `--onefile` mode (already enabled) for single-file distribution

