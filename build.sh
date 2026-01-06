#!/bin/bash
# Build script for Maple Autocuber (Linux/Mac)

echo "Building Maple Autocuber executable..."
echo

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller is not installed. Installing..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "Failed to install PyInstaller. Please install it manually: pip install pyinstaller"
        exit 1
    fi
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist __pycache__

# Build the executable
echo "Building executable..."
pyinstaller build_exe.spec

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo
echo "Build complete! Executable is in the 'dist' folder."
echo "File: dist/MapleAutocuber"
echo

