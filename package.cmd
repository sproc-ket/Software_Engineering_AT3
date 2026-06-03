@echo off
REM Package the application into a distributable Windows folder using PyInstaller.
REM This script does not modify your source files.
REM If anything goes wrong, delete the generated build artifacts and keep your original code untouched.

python -m PyInstaller --onedir --noconfirm --windowed --name MarkEstimatorApp CODE\mark_estimator_experimental.py

echo.
echo Packaging complete. If you need to reverse this, delete the following items:
echo   dist\MarkEstimatorApp
echo   build
echo   MarkEstimatorApp.spec
echo Note: your original source files in CODE\ are not modified.
pause