@echo off
echo Building Aincrad executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller. Please install it manually: pip install pyinstaller
        pause
        exit /b 1
    )
)

REM Verify Tesseract folder exists
if not exist "tesseract\tesseract.exe" (
    echo WARNING: Tesseract folder not found in tesseract/
    echo Please ensure tesseract/ contains the portable Tesseract installation
    echo The build will continue, but Tesseract must be bundled for the executable to work.
    pause
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Build the executable
echo Building executable...
pyinstaller build_exe.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build complete! Executable is in the 'dist' folder.
echo File: dist\Aincrad.exe
echo.
pause

