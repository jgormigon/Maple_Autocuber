# Release Guide

## Preparing for Release

### 1. Ensure Tesseract is Bundled

Make sure you have the portable Tesseract OCR in `tesseract/` folder at project root:
```
Aincrad/
  tesseract/
    tesseract.exe
    tessdata/
    (all DLLs and dependencies)
```

### 2. Test Local Build

Before creating a release, test the build locally:
```bash
build.bat
```

Verify that:
- The executable is created in `dist/Aincrad.exe`
- The executable runs without errors
- OCR functionality works (Tesseract is detected)

### 3. Create a Release

#### Option A: Automatic Release via GitHub Actions

1. **Create and push a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions will automatically:**
   - Build the executable
   - Create a GitHub Release
   - Upload the release archive

#### Option B: Manual Release

1. Build the executable:
   ```bash
   build.bat
   ```

2. Create a release archive:
   - Zip `dist/Aincrad.exe` (Tesseract is already bundled in the .exe)
   - Or use the release folder created by the workflow

3. Create a GitHub Release manually:
   - Go to GitHub → Releases → Draft a new release
   - Upload the zip file
   - Add release notes

## GitHub Actions Workflow

The workflow (`.github/workflows/release.yml`) automatically:

1. **Triggers on:**
   - Version tags (e.g., `v1.0.0`)
   - Manual workflow dispatch

2. **Builds:**
   - Installs Python dependencies
   - Verifies Tesseract folder exists
   - Builds executable with PyInstaller
   - Creates release archive

3. **Releases:**
   - Creates GitHub Release (for tags)
   - Uploads artifacts
   - Includes release notes

## Version Tagging

Use semantic versioning:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release
- `v1.1.1` - Patch release

Example:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Release Checklist

- [ ] Tesseract folder is in `tesseract/` at project root
- [ ] Local build succeeds
- [ ] Executable runs and OCR works
- [ ] Code is committed and pushed
- [ ] Version tag is created and pushed
- [ ] GitHub Actions workflow completes successfully
- [ ] Release notes are updated
- [ ] Release is published

## Troubleshooting

### Tesseract not found in build
- Ensure `tesseract/tesseract.exe` exists at project root
- Check that the path in `build_exe.spec` is correct: `('tesseract', 'tesseract')`

### Executable doesn't find Tesseract
- Check `tesseract_config.py` paths
- Verify Tesseract is bundled in the executable (check temp extraction folder)
- Enable console mode in `build_exe.spec` to see debug output

### GitHub Actions fails
- Check that Tesseract folder exists in the repository
- Verify Python version compatibility
- Check workflow logs for specific errors

