@echo off

title Disney's Toontown Online Alpha Game Launcher






set TTG_GAMESERVER=127.0.0.1




set /P TTG_PLAYCOOKIE=Username: 


echo.

echo ===============================
echo Starting Disney's Toontown Online...
echo ppython: "dependencies/panda/python/ppython.exe"



echo Username: %TTG_PLAYCOOKIE%


echo Gameserver: %TTG_GAMESERVER%
echo ===============================

cd ../../

:main

"dependencies/panda/python/ppython.exe" -m toontown.toonbase.ToontownStart

pause

goto main
