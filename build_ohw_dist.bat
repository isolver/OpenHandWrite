@echo off
set WINPYDIR=%~dp0OpenHandWrite\WinPython\python-2.7.10.amd64
set WINPYVER=2.7.10.2
set HOME=%WINPYDIR%\..\settings
set WINPYARCH="WIN32"
if  "%WINPYDIR:~-5%"=="amd64" set WINPYARCH="WIN-AMD64"

set PATH=%WINPYDIR%\Lib\site-packages\PyQt5;%WINPYDIR%\Lib\site-packages\PyQt4;%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts;%WINPYDIR%\..\tools;%WINPYDIR%\..\tools\mingw32\bin;%WINPYDIR%\..\tools\R\bin\x64;%WINPYDIR%\..\tools\Julia\bin;%PATH%;

echo.

set OPENHW_SRC_DIR=%~dp0..\DEV\OpenHandWrite
set OPENHW_DST_DIR=%~dp0OpenHandWrite


REM **** Not rebuilding psychopy at this time, 
REM      since the latest psychopy source breaks 
REM      iohub.wintab. See https://github.com/isolver/OpenHandWrite/issues/160
REM
REM set PSYCHOPY_SRC_DIR=%~dp0..\WinPython-32bit-2.7.6.0\my-code\psychopy
REM REM >>> Build latest PsychoPy package from local source
REM echo Building latest PsychoPy Source ...
REM cd %PSYCHOPY_SRC_DIR%
REM python setup.py install
REM cd %~dp0
REM echo.
REM REM <<<
echo IMPORTANT: Psychopy is not being updated in OpenHandWrite distribution
echo IMPORTANT: at this time. If any changes have been made to psychopy.iohub, 
echo IMPORTANT: manually update psychopy.iohub in the OpenHW/WinPython 
echo IMPORTANT: site-packages folder.
echo.
PAUSE

REM >>> Build latest markwrite package from local source
set HDF5_DISABLE_VERSION_CHECK=2
set MARKWRITE_SRC_DIR=%~dp0..\DEV\OpenHandWrite\src\markwrite
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