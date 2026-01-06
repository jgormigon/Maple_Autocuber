# Migrating Tesseract from dist/ to Project Root

If you have Tesseract in `dist/tesseract/`, follow these steps to move it to the project root:

## Steps

1. **Move the folder:**
   ```bash
   move dist\tesseract tesseract
   ```

2. **Verify the move:**
   ```bash
   dir tesseract\tesseract.exe
   ```
   Should show the file exists.

3. **Test the build:**
   ```bash
   build.bat
   ```

4. **Commit the changes:**
   ```bash
   git add tesseract/
   git commit -m "Move Tesseract folder to project root"
   ```

## What Changed

- **Old location**: `dist/tesseract/`
- **New location**: `tesseract/` (at project root)

All build scripts, documentation, and code have been updated to use the new location.

