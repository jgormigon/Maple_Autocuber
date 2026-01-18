# Build System Changes

## Summary

The build system has been updated to bundle Tesseract OCR with the executable and set up automated releases via GitHub Actions.

## Changes Made

### 1. Tesseract Bundling
- **Created `tesseract_config.py`**: Automatically detects and configures bundled Tesseract
- **Updated imports**: Added `tesseract_config` imports to `botUI.py`, `image_finder.py`, and `auto_detect_crop.py`
- **Updated `build_exe.spec`**: Includes `tesseract/` folder in the build

### 2. GitHub Actions Workflow
- **Created `.github/workflows/release.yml`**: Automated build and release pipeline
- **Triggers**: Version tags (e.g., `v1.0.0`) and manual dispatch
- **Actions**: Builds executable, creates release archive, publishes GitHub Release

### 3. Build Scripts
- **Updated `build.bat`**: Verifies Tesseract folder exists before building
- **Preserves `dist/` folder**: Doesn't delete the tesseract folder during cleanup

### 4. Documentation
- **Updated `README_BUILD.md`**: Reflects bundled Tesseract
- **Updated `QUICK_START_BUILD.md`**: Simplified instructions
- **Created `RELEASE.md`**: Release guide
- **Created `SETUP_TESSERACT.md`**: Tesseract setup instructions

### 5. Git Configuration
- **Updated `.gitignore`**: Keeps `tesseract/` folder while ignoring build artifacts

## How It Works

1. **Tesseract Detection**: `tesseract_config.py` runs on import and:
   - Checks for bundled Tesseract in PyInstaller temp directory
   - Falls back to system Tesseract if bundled not found
   - Configures `pytesseract` automatically

2. **Build Process**: PyInstaller bundles:
   - All Python code and dependencies
   - `templates/` folder (reset button image)
   - `crop_config.py` (configuration)
   - `tesseract/` folder (Tesseract OCR)

3. **Release Process**: GitHub Actions:
   - Builds executable on version tag
   - Creates release archive
   - Publishes GitHub Release with download

## Usage

### Local Build
```bash
build.bat
```

### Create Release
```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically build and release.

## Benefits

- ✅ **No Installation Required**: Users don't need to install Tesseract
- ✅ **Automated Releases**: Push a tag, get a release
- ✅ **Consistent Builds**: Same build process every time
- ✅ **Easy Distribution**: Single executable with everything bundled

