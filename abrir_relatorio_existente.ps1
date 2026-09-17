# abrir_relatorio_existente.ps1
# =============================================================================
# CASO 2: Abrir apenas o ÚLTIMO relatório que já existe (não roda NADA novo)
# =============================================================================
# Lista de relatórios mais comuns (em reports/, abrindo SEMPRE o mais recente deles,
# conforme os quais são GERADOS ANTERIORMENTE (não executamos pytest aqui — de forma
# alguma; só abrir no navegador).
#
# Estratégia para escolher qual abrir:
#   1) reports\report_completo.html          (suite completa — gerado no CASO 1)
#   2) reports\report.html                     (último gerado por pytest ini addopts)
#   3) reports\report_investimentos_FINAL.html  (9/9 passed invest)
#   4) reports\report_investimentos_COMPLETO.html
#   5) O MAIS RECENTE de reports\*.html          (fallback, pega mtime maior)
# =============================================================================

Set-Location -Path "C:\laragon\www\desafioagibank"

$candidatos = @(
    "reports\report_completo.html",
    "reports\report.html",
    "reports\report_investimentos_FINAL.html",
    "reports\report_juros_katalon_golden.html",
    "reports\report_investimentos.html"
)

$arquivoParaAbrir = $null
foreach ($arq in $candidatos) {
    if (Test-Path $arq) {
        $arquivoParaAbrir = $arq
        break
    }
}

# Fallback: procura por QUALQUER .html mais recente em reports/
if (-not $arquivoParaAbrir) {
    $maisRecente = Get-ChildItem reports\*.html -ErrorAction SilentlyContinue |
                   Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($maisRecente) {
        $arquivoParaAbrir = $maisRecente.FullName
    }
}

Write-Host ""
Write-Host "======================================================================"
Write-Host "   CASO 2: Abrir relatorio ja existente (nao executa pytest)"
Write-Host "======================================================================"

if (-not $arquivoParaAbrir) {
    Write-Host ""
    Write-Host "   ❌ Nenhum relatorio HTML encontrado em reports\ !"
    Write-Host "   Execute primeiro o CASO 1 (rodar_testes_e_gerar_relatorio_novo.cmd)"
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "   Arquivo encontrado:  $arquivoParaAbrir"
Write-Host "   Tamanho:          $([math]::Round((Get-Item $arquivoParaAbrir).Length / 1KB, 1)) KB"
Write-Host "   Modificado em:    $((Get-Item $arquivoParaAbrir).LastWriteTime.ToString('dd/MM/yyyy HH:mm:ss'))"
Write-Host "   Abrindo no navegador padrao..."
Write-Host "======================================================================"

Start-Process $arquivoParaAbrir
exit 0
