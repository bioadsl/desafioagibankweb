@echo off
REM ============================================================================
REM CASO 3: RELATORIO DE AUDITORIA DOS LOGS (quem acessou / erros / adulteração?)
REM ============================================================================
cd /d "C:\laragon\www\desafioagibank"
set PYTHONIOENCODING=utf-8

echo.
echo ============================================================================
echo    CASO 3: RELATORIO DE AUDITORIA DOS LOGS
echo ============================================================================

echo.
echo ----------------------------------------------------------------------------
echo  [1/5]  RESUMO (ultimos 7 dias)
echo ----------------------------------------------------------------------------
python reports\auditoria\auditoria_consultar.py --resumo --ultimos-dias 7

echo.
echo ----------------------------------------------------------------------------
echo  [2/5]  VALIDACAO CADEIA DE CUSTODIA SHA-256 (adulteracao? integro?)
echo ----------------------------------------------------------------------------
python reports\auditoria\auditoria_consultar.py --validar-cadeia

echo.
echo ----------------------------------------------------------------------------
echo  [3/5]  TOP 10 ERROS (ultimos 30 dias)
echo ----------------------------------------------------------------------------
python reports\auditoria\auditoria_consultar.py --top-erros --ultimos-dias 30

echo.
echo ----------------------------------------------------------------------------
echo  [4/5]  ULTIMOS 15 REGISTROS (user e IP descriptografados)
echo ----------------------------------------------------------------------------
python reports\auditoria\auditoria_consultar.py --ultimos-dias 7 --limit 15 --verbose

echo.
echo ----------------------------------------------------------------------------
echo  [5/5]  EXPORTACAO JSON (p/ Excel Power BI Grafana): reports\auditoria_export_ultimos_7dias.json
echo ----------------------------------------------------------------------------
python reports\auditoria\auditoria_consultar.py --ultimos-dias 7 --json > reports\auditoria_export_ultimos_7dias.json

echo.
echo ============================================================================
echo    ARQUIVOS GERADOS:
echo      • reports\auditoria_export_ultimos_7dias.json
echo      • reports\auditoria\data\audit_log.db
echo      • reports\auditoria\data\audit_log.jsonl
echo ============================================================================
pause
exit /b 0
