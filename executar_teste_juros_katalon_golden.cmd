@echo off
REM ============================================================================
REM executar_teste_juros_katalon_golden.cmd   (COMANDO EXECUTAVEL - Windows CMD)
REM ============================================================================
REM Mesmo padrao do exemplo usuario fornecido, formato .CMD (double-click OK).
REM Equivalente ao arquivo .PS1 PowerShell do mesmo nome.
REM ============================================================================
cd /d "C:\laragon\www\desafioagibank"
set HEADLESS=false
set SLOW_MO=400
python -m pytest tests/test_calculadora_juros.py -m katalon_golden -vs --tb=short
pause
