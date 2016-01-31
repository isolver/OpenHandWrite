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
set OPENHW_DST_DIR=%~dp0OpenHandWrite

set PSYCHOPY_SRC_DIR=%~dp0..\WinPython-32bit-2.7.6.0\my-code\psychopy
set MARKWRITE_SRC_DIR=%~dp0..\DEV\OpenHandWrite\src\markwrite
REM >>> Build latest PsychoPy package from local source
echo Building latest PsychoPy Source ...
cd %PSYCHOPY_SRC_DIR%
python setup.py install
cd %~dp0
echo.
REM <<<

set HDF5_DISABLE_VERSION_CHECK=2

REM >>> Build latest markwrite package from local source
echo Building latest markwrite Source ...
cd %MARKWRITE_SRC_DIR%
python setup.py install
cd %~dp0
echo.
REM <<<

REM >>> Copy latest OpenHandWrite distribution files to .\OpenHandWrite
echo Copying OpenHandWrite Distribution Files...
xcopy %OPENHW_SRC_DIR%\distribution %OPENHW_DST_DIR% /v /y /s /e /q /i
echo.
REM <<<

REM >>> Copy latest OpenHW wintab test script to .\OpenHandWrite\getwrite\wintabtest
echo Copying latest OpenHW psychopy.iohub wintab test script...
xcopy %PSYCHOPY_SRC_DIR%\psychopy\demos\coder\iohub\wintab\*.py %OPENHW_DST_DIR%\getwrite\wintabtest /v /y /s /e /q /i
echo.
REM <<<

PAUSE