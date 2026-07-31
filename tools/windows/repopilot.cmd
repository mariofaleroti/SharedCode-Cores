@echo off
setlocal

rem Carpeta donde se encuentra este lanzador:
rem <Proyecto>\tools\windows\
set "SCRIPT_DIR=%~dp0"

rem Resolver físicamente la raíz del proyecto, eliminando .. y la barra final.
for %%I in ("%SCRIPT_DIR%..\..") do set "PROJECT_ROOT=%%~fI"

rem RepoPilot está como proyecto hermano dentro de Proyectos.
for %%I in ("%PROJECT_ROOT%\..\RepoPilot") do set "REPOPILOT_ROOT=%%~fI"

rem Validaciones claras.
if not exist "%REPOPILOT_ROOT%\main.py" (
    echo [ERROR] No se encontro RepoPilot:
    echo         %REPOPILOT_ROOT%\main.py
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%\.git" (
    echo [ERROR] El proyecto no contiene un repositorio Git:
    echo         %PROJECT_ROOT%
    pause
    exit /b 1
)

python "%REPOPILOT_ROOT%\main.py" "%PROJECT_ROOT%"

set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo RepoPilot finalizo con codigo %EXIT_CODE%.
    pause
)

endlocal & exit /b %EXIT_CODE%