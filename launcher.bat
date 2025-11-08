@echo off
REM AI Trading Agent - Quick Launcher for Windows

:menu
cls
echo ========================================
echo     AI TRADING AGENT - LAUNCHER
echo ========================================
echo.
echo Choose an option:
echo.
echo 1. Test Signal Parser
echo 2. Dry Run (Monitor Only)
echo 3. View Portfolio Dashboard
echo 4. Paper Trading
echo 5. Live Trading (WARNING!)
echo 6. Install Dependencies
echo 7. Setup Configuration
echo 8. View Logs
echo 9. Exit
echo.
set /p choice="Enter choice (1-9): "

if "%choice%"=="1" goto test_parser
if "%choice%"=="2" goto dry_run
if "%choice%"=="3" goto dashboard
if "%choice%"=="4" goto paper_trading
if "%choice%"=="5" goto live_trading
if "%choice%"=="6" goto install
if "%choice%"=="7" goto setup
if "%choice%"=="8" goto logs
if "%choice%"=="9" goto end
goto menu

:test_parser
cls
echo Running Signal Parser Test...
echo.
python test_parser.py
pause
goto menu

:dry_run
cls
echo Starting Dry Run Monitor...
echo This will monitor your Telegram channel WITHOUT executing trades.
echo Press Ctrl+C to stop.
echo.
python dry_run.py
pause
goto menu

:dashboard
cls
echo Loading Portfolio Dashboard...
echo.
python dashboard.py
pause
goto menu

:paper_trading
cls
echo ========================================
echo      PAPER TRADING MODE
echo ========================================
echo.
echo This will execute trades using paper money.
echo Make sure TRADING_MODE=paper in your .env file
echo.
echo Press Ctrl+C to stop the agent at any time.
echo.
pause
python main.py
pause
goto menu

:live_trading
cls
echo ========================================
echo       !!! WARNING !!!
echo    LIVE TRADING MODE
echo ========================================
echo.
echo This will execute trades with REAL MONEY!
echo Make sure you have:
echo   - Tested thoroughly in paper mode
echo   - Set appropriate position sizes
echo   - Configured risk limits
echo   - TRADING_MODE=live in .env
echo.
set /p confirm="Are you SURE you want to continue? (yes/no): "
if /i not "%confirm%"=="yes" goto menu
echo.
echo Starting live trading...
echo Press Ctrl+C to stop at any time.
echo.
pause
python main.py
pause
goto menu

:install
cls
echo Installing Dependencies...
echo.
pip install -r requirements.txt
echo.
echo Done!
pause
goto menu

:setup
cls
echo ========================================
echo    CONFIGURATION SETUP
echo ========================================
echo.
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo .env file created!
    echo Please edit it with your credentials.
    echo.
    set /p edit="Open .env in notepad? (y/n): "
    if /i "%edit%"=="y" notepad .env
) else (
    echo .env file already exists.
    set /p edit="Edit .env file? (y/n): "
    if /i "%edit%"=="y" notepad .env
)
pause
goto menu

:logs
cls
echo Recent Log Files:
echo.
dir /b /o-d logs\*.log 2>nul
echo.
if errorlevel 1 (
    echo No log files found yet.
    echo Logs will be created when you run the agent.
) else (
    echo.
    set /p viewlog="View latest log? (y/n): "
    if /i "%viewlog%"=="y" (
        for /f "delims=" %%i in ('dir /b /o-d logs\*.log') do (
            notepad logs\%%i
            goto menu
        )
    )
)
pause
goto menu

:end
cls
echo.
echo Thanks for using AI Trading Agent!
echo.
timeout /t 2
exit
