# Setting Up Bundled Tesseract

## Overview

The Maple Autocuber executable bundles a portable version of Tesseract OCR so users don't need to install it separately.

## Requirements

You need a portable (standalone) version of Tesseract OCR for Windows. The portable version should:
- Not require installation
- Include all DLL dependencies
- Include the `tessdata` folder with language data

## Setup Steps

### 1. Download Portable Tesseract

Download a portable version of Tesseract OCR for Windows. You can:
- Use the official portable build from: https://github.com/UB-Mannheim/tesseract/wiki
- Or extract from an installer to create a portable version

### 2. Place in tesseract/ folder at project root

The folder structure should be:
```
Maple_Autocuber/
  tesseract/
    tesseract.exe          # Main executable
    tessdata/              # Language data folder
      eng.traineddata      # English language data (required)
      osd.traineddata       # Orientation and script detection
      (other .dll files)   # All required DLLs
    (all .dll files)       # All required DLL dependencies
```

### 3. Verify Structure

Check that:
- `tesseract/tesseract.exe` exists
- `tesseract/tessdata/eng.traineddata` exists
- All required DLLs are present

### 4. Commit to Repository

The `tesseract/` folder should be committed to your repository:
```bash
git add tesseract/
git commit -m "Add bundled Tesseract OCR"
```

The `.gitignore` is configured to ignore build artifacts but keep the `tesseract/` folder.

## Testing

After setting up, test that Tesseract works:

1. **Test locally:**
   ```bash
   tesseract\tesseract.exe --version
   ```

2. **Test in Python:**
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'tesseract\tesseract.exe'
   print(pytesseract.get_tesseract_version())
   ```

3. **Test build:**
   ```bash
   build.bat
   ```
   The build should automatically include the Tesseract folder.

## GitHub Actions

The GitHub Actions workflow will:
1. Verify that `tesseract/tesseract.exe` exists
2. Bundle it with the executable during build
3. Create a release with the bundled executable

## Troubleshooting

### Tesseract not found during build
- Ensure `tesseract/tesseract.exe` exists
- Check file permissions
- Verify the path in `build_exe.spec`: `('tesseract', 'tesseract')`

### Executable can't find Tesseract
- Check `tesseract_config.py` paths
- Verify Tesseract is bundled (check PyInstaller temp folder)
- Enable console mode to see debug output

### Missing DLL errors
- Ensure all required DLLs are in `tesseract/`
- Check Tesseract dependencies
- Test the portable Tesseract standalone first

## File Size

The bundled Tesseract adds significant size (~50-100MB) to the executable. This is normal and expected. The total executable size will be:
- Base executable: ~50-100MB
- Bundled Tesseract: ~50-100MB
- **Total: ~100-200MB**

This is acceptable for a standalone application that doesn't require any external dependencies.

