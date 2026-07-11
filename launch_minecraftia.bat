@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
set "MINECRAFT_WORLD_PATH=D:\Minecraft Worlds\saves\city1mansion ai"
cd /d "%PROJECT_ROOT%"
python -m src.main
pause
