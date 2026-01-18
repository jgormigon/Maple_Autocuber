# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file
"""

block_cipher = None

a = Analysis(
    ['src/botUI.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),  # Include templates folder (reset_button.jpg)
        ('tesseract', 'tesseract'),  # Include bundled Tesseract OCR
    ],
    hiddenimports=[
        'win32gui',
        'win32api',
        'win32con',
        'pytesseract',
        'src.tesseract_config',  # Tesseract configuration module
        'src.crop_config',  # Crop configuration module
        'src.bot_logic',
        'src.translate_ocr_results',
        'src.macro_controls',
        'src.image_finder',
        'src.image_processing',
        'src.windowcapture',
        'src.auto_detect_crop',
        'cv2',
        'numpy',
        'PIL',
        'PIL._tkinter_finder',
        'pyautogui',
        'keyboard',
        'mss',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'threading',
        're',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Aincrad',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one: 'icon.ico'
)

