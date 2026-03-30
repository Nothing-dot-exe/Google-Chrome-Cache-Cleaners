@echo off
title Clear Google Chrome Cache
echo ==========================================
echo       Clearing Google Chrome Cache
echo ==========================================
echo.
echo Closing Google Chrome...
taskkill /F /IM chrome.exe >nul 2>&1

:: Wait a second for processes to close
timeout /t 2 /nobreak >nul

set "USER_DATA=%LOCALAPPDATA%\Google\Chrome\User Data"

if not exist "%USER_DATA%" (
    echo Chrome User Data directory not found!
    echo Are you sure Google Chrome is installed?
    echo.
    pause
    exit /b
)

echo.
echo Deleting cache files...

:: Clear cache for Default profile
if exist "%USER_DATA%\Default\Cache" rmdir /s /q "%USER_DATA%\Default\Cache" >nul 2>&1
if exist "%USER_DATA%\Default\Code Cache" rmdir /s /q "%USER_DATA%\Default\Code Cache" >nul 2>&1
if exist "%USER_DATA%\Default\GPUCache" rmdir /s /q "%USER_DATA%\Default\GPUCache" >nul 2>&1

:: Clear cache for other profiles (Profile 1, Profile 2, etc.)
for /d %%D in ("%USER_DATA%\Profile *") do (
    if exist "%%D\Cache" rmdir /s /q "%%D\Cache" >nul 2>&1
    if exist "%%D\Code Cache" rmdir /s /q "%%D\Code Cache" >nul 2>&1
    if exist "%%D\GPUCache" rmdir /s /q "%%D\GPUCache" >nul 2>&1
)

:: Clear general caches
if exist "%USER_DATA%\ShaderCache" rmdir /s /q "%USER_DATA%\ShaderCache" >nul 2>&1
if exist "%USER_DATA%\GrShaderCache" rmdir /s /q "%USER_DATA%\GrShaderCache" >nul 2>&1
if exist "%USER_DATA%\System Profile\Cache" rmdir /s /q "%USER_DATA%\System Profile\Cache" >nul 2>&1

echo.
echo ==========================================
echo   Chrome Cache successfully cleared!
echo ==========================================
echo.
pause
