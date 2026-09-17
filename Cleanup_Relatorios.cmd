@echo off
REM ==========================================================================
REM   Cleanup_Relatorios.cmd  —  Cleanup de relatórios (2 cliques Windows Explorer)
REM   Padrão exato igual aos outros arquivos Caso_X_*.cmd do projeto.
REM ==========================================================================
REM   Menu interativo:
REM     1) SIMULAR (Dry-run) → padrão, NÃO APAGA NADA, lista tudo
REM     2) EXECUTAR DE VERDADE (apaga arquivos, modo -Force, pergunta confirmar)
REM     3) EXECUTAR com retenção LGPD customizada (padrão 90 dias → usuário digita 30)
REM ==========================================================================
title Cleanup Relatorios Desafio Agibank
chcp 65001 >nul 2>&1
setlocal enableextensions enabledelayedexpansion
set "PYTHONIOENCODING=utf-8"
set "HEADLESS=true"
set "SLOW_MO=0"
cd /d "%~dp0"

:MENU_PRINCIPAL
cls
echo.
echo ====================================================================================
echo           🧹 CLEANUP DE RELATORIOS — DESAFIO AGIBANK
echo ====================================================================================
echo.
echo   Escolha uma opcao (1 / 2 / 3 / S):
echo.
echo      [1]  🔍  SIMULACAO (DRY-RUN) — NAO APAGA NADA (padrao recomendado)
echo                    Lista TUDO o que seria removido + tamanho em MB.
echo.
echo      [2]  🔥  EXECUCAO REAL — APAGA arquivos marcados (pergunta confirma)
echo                    Retencao LGPD auditoria: 90 dias (default).
echo.
echo      [3]  🔥  EXECUCAO REAL COM RETENCAO CUSTOM
echo                    (Voce digita N dias de retencao LGPD ex: 30)
echo.
echo      [S]  ❌  SAIR
echo.
echo ====================================================================================
set /p OPCAO="         Digite sua opcao e pressione ENTER [padrao = 1 simulacao]: "
if "%OPCAO%"=="" set OPCAO=1
if /i "%OPCAO%"=="S" goto SAIR
if "%OPCAO%"=="1" goto MODO_SIMULACAO
if "%OPCAO%"=="2" goto MODO_REAL_90
if "%OPCAO%"=="3" goto MODO_REAL_CUSTOM
echo.
echo   [ERRO] Opcao invalida: "%OPCAO%". Tente novamente.
pause
goto MENU_PRINCIPAL

:SAIR
cls
echo.
echo   Saindo sem executar nada.
timeout /t 2 >nul 2>&1
exit /b 0

:MODO_SIMULACAO
cls
echo.
echo   *********************************************************************************
echo   * 🔍 MODO SIMULACAO (Dry-run):  NAO SERA APAGADO NENHUM ARQUIVO
echo   *********************************************************************************
echo.
echo   Chamando: powershell -ExecutionPolicy Bypass -File .\cleanup_relatorios.ps1
echo   (sem parametros - o default do script = Dry-run)
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\cleanup_relatorios.ps1"
echo.
echo   Pressione qualquer tecla para voltar ao MENU PRINCIPAL...
pause >nul
goto MENU_PRINCIPAL

:MODO_REAL_90
cls
echo.
echo   *********************************************************************************
echo   * 🔥 MODO EXECUCAO REAL — -Force + Retencao LGPD 90 DIAS (padrao)
echo   *********************************************************************************
echo.
echo   ATENCAO: Arquivos marcados SERAO APAGADOS de forma irreversivel.
echo            O script pede confirmacao final ANTES de apagar.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\cleanup_relatorios.ps1" -Force
echo.
echo   Pressione qualquer tecla para voltar ao MENU PRINCIPAL...
pause >nul
goto MENU_PRINCIPAL

:MODO_REAL_CUSTOM
cls
echo.
set "DIAS_LGPD="
echo   *********************************************************************************
echo   * 🔥 MODO EXECUCAO REAL — -Force + Retencao LGPD CUSTOMIZADA
echo   *********************************************************************************
echo.
set /p DIAS_LGPD="         Digite quantos dias de retencao LGPD p/ logs de auditoria (ex: 30 ou 90): "
if "%DIAS_LGPD%"=="" set DIAS_LGPD=90
for /f "delims=0123456789" %%i in ("%DIAS_LGPD%") do (
  echo   [ERRO] Valor invalido: "%DIAS_LGPD%" — digite APENAS numeros.
  pause
  goto MODO_REAL_CUSTOM
)
if %DIAS_LGPD% LSS 1 (
  echo   [ERRO] Dias minimo = 1. Usando 1.
  set DIAS_LGPD=1
)
echo.
echo   --- Usando retencao LGPD = %DIAS_LGPD% dias para logs auditoria.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\cleanup_relatorios.ps1" -Force -RetencaoDias %DIAS_LGPD%
echo.
echo   Pressione qualquer tecla para voltar ao MENU PRINCIPAL...
pause >nul
goto MENU_PRINCIPAL

endlocal
exit /b 0
