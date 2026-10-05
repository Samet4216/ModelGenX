@echo off
title ModelGenX Baslatici
echo =======================================
echo     ModelGenX Sanal Ortami Yukleniyor
echo =======================================

:: Sanal ortami aktif et
call genx\Scripts\activate.bat

:: Uygulamayi baslat
echo ModelGenX baslatiliyor...
python main.py

echo.
pause
