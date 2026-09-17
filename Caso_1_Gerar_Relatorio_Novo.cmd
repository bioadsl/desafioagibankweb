@echo off
REM ============================================================================
REM CASO 1: RODAR TODOS OS TESTES E GERAR RELATORIO NOVO
REM (2 cliques no Explorer - duplo clique neste arquivo)
REM ============================================================================
cd /d "C:\laragon\www\desafioagibank"
set HEADLESS=true
set SLOW_MO=0
set PYTHONIOENCODING=utf-8

echo.
echo ============================================================================
echo    CASO 1: Rodando TODOS os testes e GERANDO RELATORIO NOVO...
echo ============================================================================
echo.

python -m pytest ^
    tests/test_calculadora_dias_uteis.py ^
    tests/test_calculadora_juros.py ^
    tests/test_calculadora_investimentos.py ^
    tests/test_blog_agi.py ^
    tests/test_auditoria_relatorios.py ^
    --html=reports\report_completo.html ^
    --self-contained-html ^
    --capture=tee-sys ^
    -v ^
    --tb=short

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================================================
echo    Relatorio gerado:  reports\report_completo.html
echo    Exit code pytest:  %EXIT_CODE%
echo    Abrindo no navegador padrao...
echo ============================================================================

start "" "reports\report_completo.html"
pause
exit /b %EXIT_CODE%
