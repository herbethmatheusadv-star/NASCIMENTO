@echo off
chcp 65001 >nul
title SOJ - Painel do dia  (deixe esta janela aberta)
cd /d "%~dp0"
echo.
echo   ================================================================
echo     SOJ - PAINEL DO DIA
echo   ================================================================
echo     Abrindo no seu navegador...
echo     Deixe ESTA janela aberta enquanto usa o painel.
echo     Para encerrar: feche esta janela (ou tecle Ctrl+C).
echo   ================================================================
echo.
python ESCRITORIO\scripts\soj_servidor.py
echo.
echo   [painel encerrado]
pause
