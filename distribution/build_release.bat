@echo off
set WINPYDIR=%~dp0OpenHandWrite\WinPython\python-2.7.10.amd64
set WINPYVER=2.7.10.2
set HOME=%WINPYDIR%\..\settings
set WINPYARCH="WIN32"
if  "%WINPYDIR:~-5%"=="amd64" set WINPYARCH="WIN-AMD64"

rem handle R if included
if not exist "%WINPYDIR%\..\tools\R\bin" goto r_bad
set R_HOME=%WINPYDIR%\..\tools\R
if %WINPYARCH%=="WIN32"     set R_HOMEbin=%R_HOME%\bin\i386
if not %WINPYARCH%=="WIN32" set R_HOMEbin=%R_HOME%\bin\x64
:r_bad

rem handle Julia if included
if not exist "%WINPYDIR%\..\tools\Julia\bin" goto julia_bad
set JULIA_HOME=%WINPYDIR%\..\tools\Julia\bin\
set JULIA_EXE=julia.exe
set JULIA=%JULIA_HOME%%JULIA_EXE%
set JULIA_PKGDIR=%WINPYDIR%\..\settings\.julia
:julia_bad

set PATH=%WINPYDIR%\Lib\site-packages\PyQt5;%WINPYDIR%\Lib\site-packages\PyQt4;%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts;%WINPYDIR%\..\tools;%WINPYDIR%\..\tools\mingw32\bin;%WINPYDIR%\..\tools\R\bin\x64;%WINPYDIR%\..\tools\Julia\bin;%PATH%;

echo.

set OPENHW_SRC_DIR=%~dp0..\DEV\OpenHandWrite
set PSYCHOPY_SRC_DIR=%~dp0..\WinPython-32bit-2.7.6.0\my-code\psychopy
 
REM >>> Build latest PsychoPy package from local source
echo Building latest PsychoPy Source ...
cd %PSYCHOPY_SRC_DIR%
python setup.py install
cd %~dp0
echo.
REM <<<

REM >>> Copy latest OpenHW getwrite files to .\OpenHandWrite\getwrite
echo Copying OpenHW getwrite Files...
xcopy %OPENHW_SRC_DIR%\getwrite %~dp0OpenHandWrite\getwrite /v /y /s /e /q /i
echo.
REM <<<

REM >>> Copy latest OpenHW wintab test script to .\OpenHandWrite\getwrite
echo Copying latest OpenHW psychopy.iohub wintab test script...
xcopy %PSYCHOPY_SRC_DIR%\psychopy\demos\coder\iohub\wintab\*.py %~dp0OpenHandWrite\getwrite\wintabtest /v /y /s /e /q /i
echo.
REM <<<

REM >>> Copy latest OpenHW markwrite files to .\OpenHandWrite\markwrite
echo Copying OpenHW markwrite Files...
xcopy %OPENHW_SRC_DIR%\markwrite %~dp0OpenHandWrite\markwrite /v /y /s /e /q /i
echo.
REM <<<

REM >>> Copy .bat launcher files to .\OpenHandWrite
echo Copying .bat launcher files...
copy %OPENHW_SRC_DIR%\distribution\launchers\*.bat %~dp0OpenHandWrite  /v /y
echo.
REM <<<

PAUSE