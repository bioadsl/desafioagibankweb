@echo off
REM ============================================================================
REM CASO 2: ABRIR O ULTIMO RELATORIO JA EXISTENTE (NAO roda pytest novo!)
REM ============================================================================
cd /d "C:\laragon\www\desafioagibank"

set ARQ_ABRIR=

REM Ordem de preferencia: o primeiro que existir
for %%f in (
    reports\report_completo.html
    reports\report.html
    reports\report_investimentos_FINAL.html
    reports\report_juros_katalon_golden.html
    reports\report_investimentos.html
) do (
    if exist "%%f" (
        set "ARQ_ABRIR=%%f"
        goto :encontrado
    )
)

REM Fallback: pega o .html mais recente da pasta reports (qualquer um)
for /f "delims=" %%a in ('dir /b /o:-d reports\*.html 2^>nul') do (
    set "ARQ_ABRIR=reports\%%a"
    goto :encontrado
)

:nao_encontrado
echo.
echo ============================================================================
echo    ❌ Nenhum relatorio HTML encontrado em reports\ !
echo    Primeiro execute o CASO 1:
echo       Caso_1_Gerar_Relatorio_Novo.cmd
echo ============================================================================
echo.
pause
exit /b 1

:encontrado
echo.
echo ============================================================================
echo    CASO 2: Abrir relatorio JA EXISTENTE
echo    Arquivo:  %ARQ_ABRIR%
echo ============================================================================
start "" "%ARQ_ABRIR%"
exit /b 0
