@echo off
echo Fixing code formatting with black...

REM Use WinPython directly
"C:\Users\sahoo\winpython\WPy64-31201b5\python-3.12.0.amd64\python.exe" -m black .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Code formatted successfully!
    echo Committing changes...
    git add .
    git commit -m "Apply black formatting fixes to all files"
    git push origin main
) else (
    echo ❌ Black formatting failed!
)

pause
