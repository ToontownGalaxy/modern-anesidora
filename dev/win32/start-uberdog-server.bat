@echo off

title TTG Uberdog
rem Define some constants for our UberDOG server:
set MAX_CHANNELS=999999
set STATESERVER=4002
set ASTRON_IP=127.0.0.1:7100
set EVENTLOGGER_IP=127.0.0.1:7198
set BASE_CHANNEL=1000000

echo ===============================
echo ppython: "dependencies/panda/python/ppython.exe"
REM echo Base channel: %BASE_CHANNEL%
REM echo Max channels: %MAX_CHANNELS%
REM echo State Server: %STATESERVER%
REM echo Astron IP: %ASTRON_IP%
REM echo Event Logger IP: %EVENTLOGGER_IP%
echo ===============================

cd ../../


:main
"dependencies/panda/python/ppython.exe" ^
	-m toontown.uberdog.UDStart

pause
goto main


