@echo off
cd "../../dependencies/astron/"

title TTG Astron
:main
astrond --loglevel info --pretty config/cluster.yml
pause
goto :main
