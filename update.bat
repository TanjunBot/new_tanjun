@echo off
setlocal enabledelayedexpansion

:: Load environment variables from .env file
for /f "tokens=1,2 delims==" %%i in ('type C:\path\to\.env') do (
    set "%%i=%%j"
)

:: Check the value of APPLICATION_ID and navigate accordingly
if "%APPLICATION_ID%"=="885984139315122206" (
    echo Navigating to C:\path\to\tanjun...
    cd /d C:\path\to\tanjun
    call C:\path\to\python\Scripts\activate.bat
    net stop tanjun
) else if "%APPLICATION_ID%"=="1000673977406070864" (
    echo Navigating to C:\path\to\sayoka...
    cd /d C:\path\to\sayoka
    call C:\path\to\python\Scripts\activate.bat
    net stop sayoka
) else if "%APPLICATION_ID%"=="1255607578722046015" (
    echo Navigating to C:\path\to\demo-tanjun...
    cd /d C:\path\to\demo-tanjun
    call C:\path\to\python\Scripts\activate.bat
    net stop demo-tanjun
) else (
    echo Unknown APPLICATION_ID: %APPLICATION_ID%
    exit /b 1
)

:: Confirm the current directory
echo Current directory: %cd%

:: Pull latest changes from Git and install dependencies
git pull
pip install -r requirements.txt

echo Update completed successfully. Starting bot...

:: Restart the appropriate service
if "%APPLICATION_ID%"=="885984139315122206" (
    net start tanjun
) else if "%APPLICATION_ID%"=="1000673977406070864" (
    net start sayoka
) else if "%APPLICATION_ID%"=="1255607578722046015" (
    net start demo-tanjun
)

echo Bot started successfully.
