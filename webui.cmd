@echo off
setlocal

REM Create venv if it doesn't exist
if not exist "venv" (
    echo 'venv' not found. Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

REM Check if Python in venv works
venv\Scripts\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo 'venv\Scripts\python.exe' is not working or not found.
    exit /b 1
)

REM Install requirements if the file exists
if exist "requirements.txt" (
    echo Installing missing requirements from requirements.txt...
    venv\Scripts\python.exe -m pip install --upgrade pip >nul
    venv\Scripts\pip.exe install -r requirements.txt
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

REM Run the Gradio app
echo Running app.py using venv...
venv\Scripts\python.exe app.py

