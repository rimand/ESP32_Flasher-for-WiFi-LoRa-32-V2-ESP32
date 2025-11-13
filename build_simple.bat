@echo off
echo Building ESP32 Flasher EXE...
echo.

python -m pip install pyinstaller

pyinstaller --onefile --windowed --name "ESP32_Flasher" main.py

echo.
echo Done! Check the 'dist' folder for ESP32_Flasher.exe
pause

