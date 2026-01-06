@echo off
echo Migrating Tesseract folder from dist/ to project root...
echo.

if not exist "dist\tesseract" (
    echo ERROR: dist\tesseract folder not found!
    echo If Tesseract is already in tesseract/, you can skip this migration.
    pause
    exit /b 1
)

if exist "tesseract" (
    echo WARNING: tesseract folder already exists at project root!
    echo Please remove it first or rename it if you want to keep both.
    pause
    exit /b 1
)

echo Moving dist\tesseract to tesseract...
move dist\tesseract tesseract

if errorlevel 1 (
    echo ERROR: Failed to move folder!
    pause
    exit /b 1
)

echo.
echo Migration complete!
echo Tesseract is now at: tesseract\
echo.
echo Verifying...
if exist "tesseract\tesseract.exe" (
    echo SUCCESS: tesseract\tesseract.exe found!
) else (
    echo WARNING: tesseract\tesseract.exe not found - please verify manually
)

echo.
pause

