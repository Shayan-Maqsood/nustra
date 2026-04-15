@echo off
title NUSTra - NUST Retrieval Assistant
color 0A

set TRANSFORMERS_OFFLINE=1
set HF_HUB_OFFLINE=1

echo  NUST Retrieval Assistant — Offline AI Chatbot
echo  -----------------------------------------------
echo.

echo [1/3] Checking Ollama is running...
ollama list >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Ollama is not running or not installed.
    echo  Please install Ollama from https://ollama.com and run: ollama pull qwen2.5:3b
    pause
    exit /b 1
)
echo  Ollama OK

echo.
echo [2/3] Activating virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo  ERROR: Virtual environment not found.
    echo  Please run: python -m venv venv
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
echo  Virtual environment OK

echo.
echo [3/3] Launching NUSTra...
echo  Opening browser at http://127.0.0.1:7860
echo.
python app/chat.py

pause