@echo off
echo ========================================
echo ESP32 Flasher - Build EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo Installing/Updating PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo Building EXE file...
echo.

REM Build with PyInstaller
pyinstaller --onefile ^
    --windowed ^
    --name "ESP32_Flasher" ^
    --icon=NONE ^
    --add-data "requirements.txt;." ^
    --hidden-import=serial.tools.list_ports ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.messagebox ^
    --clean ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo EXE file location: dist\ESP32_Flasher.exe
echo.
pause

