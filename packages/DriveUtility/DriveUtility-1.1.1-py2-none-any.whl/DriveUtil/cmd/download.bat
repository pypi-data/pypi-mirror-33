@echo off

chcp 1252
title DriveUtil
cd "%~dp0..\..\"
python DriveUtil -g %*
pause