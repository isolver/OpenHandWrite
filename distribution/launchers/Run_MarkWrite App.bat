@echo off
set WINPYDIR=%~dp0WinPython\python-2.7.10.amd64
set WINPYVER=2.7.10.2
set HOME=%WINPYDIR%\..\settings
set WINPYARCH="WIN32"
if  "%WINPYDIR:~-5%"=="amd64" set WINPYARCH="WIN-AMD64"

set PATH=%WINPYDIR%\Lib\site-packages\PyQt5;%WINPYDIR%\Lib\site-packages\PyQt4;%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts;%WINPYDIR%\..\tools;%WINPYDIR%\..\tools\mingw32\bin;

set HDF5_DISABLE_VERSION_CHECK=2
cd "%~dp0markwrite
python.exe runapp.py %*

PAUSE