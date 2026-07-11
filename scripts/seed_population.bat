@echo off
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%~dp0.."
rem Activate venv if present
if exist "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
  call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
)

rem Allow overriding world path via env
if not defined MINECRAFT_WORLD_PATH (
  set "MINECRAFT_WORLD_PATH=D:\Minecraft Worlds\saves\city1mansion ai"
)

python "%~dp0seed_population.py" --world-path "%MINECRAFT_WORLD_PATH%"
