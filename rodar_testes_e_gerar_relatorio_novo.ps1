# rodar_testes_e_gerar_relatorio_novo.ps1
# =============================================================================
# CASO 1: Rodar TODOS os testes e GERAR RELATÓRIO NOVO
# =============================================================================
# Comando completo: executa os 35 testes cadastrados no projeto
#   - Dias Úteis / Juros Compostos (Aba Dívida + Investimento) /
#     Calculadora Investimentos / Blog Pesquisa / Sistema Auditoria.
#   - Gera o arquivo: reports\report_completo.html (formato self-contained:
#     pode anexar em e-mail/whatsapp sem perder formatação).
#   - No final, ABRE AUTOMATICAMENTE o relatório no navegador padrão.
#
# Obs: variáveis de ambiente HEADLESS e SLOW_MO iguais aos exemplos anteriores.
# =============================================================================

Set-Location -Path "C:\laragon\www\desafioagibank"
$env:HEADLESS = "true"
$env:SLOW_MO = "0"
$env:PYTHONIOENCODING = "utf-8"

Write-Host ""
Write-Host "======================================================================"
Write-Host "   CASO 1: Rodando TODOS os testes + gerando relatorio NOVO..."
Write-Host "======================================================================"
Write-Host ""

python -m pytest `
    tests/test_calculadora_dias_uteis.py `
    tests/test_calculadora_juros.py `
    tests/test_calculadora_investimentos.py `
    tests/test_blog_agi.py `
    tests/test_auditoria_relatorios.py `
    --html=reports\report_completo.html `
    --self-contained-html `
    --capture=tee-sys `
    -v `
    --tb=short

$exitCode = $LASTEXITCODE
Write-Host ""
Write-Host "======================================================================"
Write-Host "   Relatorio gerado:  reports\report_completo.html"
Write-Host "   Exit code pytest:  $exitCode"
Write-Host "   Abrindo no navegador padrao..."
Write-Host "======================================================================"
Start-Process reports\report_completo.html
exit $exitCode
