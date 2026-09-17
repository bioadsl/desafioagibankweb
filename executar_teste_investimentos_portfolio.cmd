@echo off
REM ============================================================================
REM executar_teste_investimentos_portfolio.cmd  (NOVO - Windows CMD executavel)
REM ============================================================================
REM MESMA ESTRUTURA, MESMAS VARIAVEIS, MESMAS FLAGS do comando juros original.
REM Apenas muda: arquivo de testes + marker portfolio (cenario GOLDEN invest)
REM ============================================================================
cd /d "C:\laragon\www\desafioagibank"
set HEADLESS=false
set SLOW_MO=400
python -m pytest tests/test_calculadora_investimentos.py -m portfolio -vs --tb=short
pause
