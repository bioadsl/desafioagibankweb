# relatorio_auditoria_logs.ps1
# =============================================================================
# CASO 3 - Relatorio de AUDITORIA DOS LOGS - 5 etapas
# =============================================================================

Set-Location -Path "C:\laragon\www\desafioagibank"
$env:PYTHONIOENCODING = "utf-8"

$SEP = "=" * 90
Write-Host ""
Write-Host $SEP
Write-Host "   CASO 3: RELATORIO DE AUDITORIA DOS LOGS"
Write-Host $SEP

Write-Host ""
Write-Host ">> 1) RESUMO ULTIMOS 7 DIAS"
Write-Host ("-" * 60)
python reports\auditoria\auditoria_consultar.py --resumo --ultimos-dias 7

Write-Host ""
Write-Host ">> 2) VALIDACAO CADEIA DE CUSTODIA SHA-256"
Write-Host ("-" * 60)
python reports\auditoria\auditoria_consultar.py --validar-cadeia

Write-Host ""
Write-Host ">> 3) TOP 10 ERROS - ultimos 30 dias"
Write-Host ("-" * 60)
python reports\auditoria\auditoria_consultar.py --top-erros --ultimos-dias 30

Write-Host ""
Write-Host ">> 4) ULTIMOS 15 REGISTROS (user e IP descriptografados)"
Write-Host ("-" * 60)
python reports\auditoria\auditoria_consultar.py --ultimos-dias 7 --limit 15 --verbose

Write-Host ""
Write-Host ">> 5) EXPORTANDO JSON: reports\auditoria_export_ultimos_7dias.json"
Write-Host ("-" * 60)
python reports\auditoria\auditoria_consultar.py --ultimos-dias 7 --json |
    Tee-Object -FilePath reports\auditoria_export_ultimos_7dias.json

Write-Host ""
Write-Host $SEP
Write-Host "   ARQUIVOS GERADOS:"
Write-Host "      - reports\auditoria_export_ultimos_7dias.json"
Write-Host "      - reports\auditoria\data\audit_log.db"
Write-Host "      - reports\auditoria\data\audit_log.jsonl"
Write-Host $SEP
pause
exit 0
