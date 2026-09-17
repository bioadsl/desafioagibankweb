# ==========================================================================
# cleanup_relatorios.ps1 - Cleanup Inteligente de Relatorios do Desafio Agibank
# ==========================================================================
# Modos de uso:
#   DRY-RUN (PADRAO - NAO APAGA):
#     powershell -ExecutionPolicy Bypass -File .\cleanup_relatorios.ps1
#   EXECUCAO REAL (APAGA):
#     powershell -ExecutionPolicy Bypass -File .\cleanup_relatorios.ps1 -Force
#   EXECUCAO SEM CONFIRMACAO (CI/CD):
#     powershell -ExecutionPolicy Bypass -File .\cleanup_relatorios.ps1 -Force -Confirm:$false
#   RETENCAO LGPD CUSTOMIZADA (30 dias):
#     powershell -File .\cleanup_relatorios.ps1 -Force -RetencaoDias 30
# ==========================================================================
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [switch]$Force = $false,
    [ValidateRange(1, 3650)]
    [int]$RetencaoDias = 90
)
$ErrorActionPreference = "Stop"

# ---------- Caminhos ---------------------------------------------------------
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPORTS = Join-Path $ROOT "reports"
$AUDIT_DIR = Join-Path $REPORTS "auditoria"
$SCREENSHOTS_DIR = Join-Path $REPORTS "screenshots"
$AUDIT_DATA = Join-Path $AUDIT_DIR "data"
$AUDIT_KEYS = Join-Path $AUDIT_DATA "keys"
$AUDIT_EXPORTS = Join-Path $AUDIT_DIR "relatorios_extraidos"

# ---------- Arquivos PROTEGIDOS (nunca apagar) ---------------------------
$ARQUIVOS_PROTEGIDOS = @(
    ".gitkeep",
    "README.md",
    "__init__.py",
    "auditor_logger.py",
    "auditoria_consultar.py",
    "auditoria_retencao_lgpd.py",
    "_resumo_auditoria_executar.py",
    "screenshot_utils.py",
    "_tmp_valida_report.py"
)

# ---------- Banner ----------------------------------------------------
$SEP = "=" * 92
Write-Host
Write-Host $SEP -ForegroundColor DarkCyan
Write-Host ("{0,82} - CLEANUP DE RELATORIOS DESAFIO AGIBANK" -f "[*]") -ForegroundColor Cyan
Write-Host $SEP -ForegroundColor DarkCyan
Write-Host (" ROOT:            {0}" -f $ROOT)
Write-Host (" Reports dir:     {0}" -f $REPORTS)

if ($Force) {
    Write-Host " Modo:            [EXECUCAO REAL - VAZ APAGAR ARQUIVOS)" -ForegroundColor Red
} else {
    Write-Host " Modo:            [DRY-RUN - SIMULACAO, NAO APAGA NADA)" -ForegroundColor Yellow
}
Write-Host (" Retencao LGPD:   $RetencaoDias dias (logs auditoria)" )
Write-Host $SEP -ForegroundColor DarkCyan
Write-Host

if (-not (Test-Path -LiteralPath $REPORTS)) {
    Write-Host "[INFO] Pasta reports/ nao existe - nada a fazer." -ForegroundColor Green
    exit 0
}

# ---------- Helpers -------------------------------------------------------
function FormatarTamanho {
    param([long]$bytes)
    if ($bytes -ge 1GB) { return ("{0:N2} GB" -f ($bytes / 1GB)) }
    if ($bytes -ge 1MB) { return ("{0:N2} MB" -f ($bytes / 1MB)) }
    if ($bytes -ge 1KB) { return ("{0:N2} KB" -f ($bytes / 1KB)) }
    return "$bytes B"
}

function Testa-ArquivoProtegido {
    param([string]$CaminhoCompleto)
    $nome = [IO.Path]::GetFileName($CaminhoCompleto)
    if ([string]::IsNullOrEmpty($nome)) { return $false }
    if ($ARQUIVOS_PROTEGIDOS -contains $nome) { return $true }
    # Chaves criptografia (.key)
    try {
        $chaves = Get-ChildItem -LiteralPath $AUDIT_KEYS -Filter "*.key" -File -ErrorAction SilentlyContinue
        foreach ($k in $chaves) {
            if ([IO.Path]::GetFullPath($k.FullName) -ieq [IO.Path]::GetFullPath($CaminhoCompleto)) {
                return $true
            }
        }
    } catch {}
    return $false
}

function Processar-Arquivos {
    param(
        [string]$Descricao,
        [string]$CaminhoPasta,
        [string[]]$Padroes,
        [int]$MaisVelhoQueDias = 0
    )
    $removiveis = New-Object System.Collections.ArrayList
    if (-not (Test-Path -LiteralPath $CaminhoPasta)) {
        Write-Host ("  [SKIP] Pasta nao encontrada: {0}" -f $CaminhoPasta) -ForegroundColor DarkGray
        return (,$removiveis)
    }
    $limiteData = (Get-Date).AddDays(-$MaisVelhoQueDias)
    foreach ($padrao in $Padroes) {
        try {
            $itens = Get-ChildItem -LiteralPath $CaminhoPasta -Filter $padrao -File -ErrorAction SilentlyContinue
        } catch { continue }
        foreach ($f in $itens) {
            if (Testa-ArquivoProtegido $f.FullName) {
                $rp = $f.FullName.Replace($ROOT, ".")
                Write-Host ("    [PROTEGIDO] {0}" -f $rp) -ForegroundColor Magenta
                continue
            }
            if ($MaisVelhoQueDias -gt 0 -and $f.LastWriteTime -gt $limiteData) {
                Write-Host ("    [RETIDO LGPD {0}d] {1}" -f $RetencaoDias, $f.Name) -ForegroundColor DarkGray
                continue
            }
            [void]$removiveis.Add($f)
        }
    }
    return (,$removiveis)
}

# ---------- CATEGORIAS DE LIMPEZA -----------------------------------------
$CATEGORIAS = @(
    @{
        Descricao = "1) Reports HTML, ZIPs trace, JSON, TXT, MD, LOG, OUT em reports/"
        Pasta     = $REPORTS
        Padroes   = @("*.html","*.zip","*.json","*.txt","*.md","*.log","*.out")
        RetDias   = 0
    },
    @{
        Descricao = "2) Screenshots PNG, JPG, WEBP, BMP em reports/screenshots/"
        Pasta     = $SCREENSHOTS_DIR
        Padroes   = @("*.png","*.jpg","*.jpeg","*.webp","*.bmp")
        RetDias   = 0
    },
    @{
        Descricao = "3) Auditoria logs JSONL + SQLite em reports/auditoria/data/"
        Pasta     = $AUDIT_DATA
        Padroes   = @("*.jsonl","*.db","*.sqlite3","*.sqlite","*.csv")
        RetDias   = $RetencaoDias
    },
    @{
        Descricao = "4) Auditoria: exports JSON CSV XLSX em reports/auditoria/relatorios_extraidos/"
        Pasta     = $AUDIT_EXPORTS
        Padroes   = @("*.json","*.csv","*.xlsx","*.html","*.txt","*.md","*.zip")
        RetDias   = 0
    },
    @{
        Descricao = "5) Auditoria __pycache__ em reports/auditoria/"
        Pasta     = (Join-Path $AUDIT_DIR "__pycache__")
        Padroes   = @("*.pyc","*.pyo")
        RetDias   = 0
    }
)

# ---------- ANALISE ---------------------------------------------
$TOTAL_TAMANHO = [long]0
$TOTAL_QTD = 0
$MAPA_CATEGORIA_ARQUIVOS = @{}

Write-Host " --- Analisando arquivos por categoria..." -ForegroundColor Cyan
Write-Host

foreach ($cat in $CATEGORIAS) {
    Write-Host (" {0}" -f $cat.Descricao) -ForegroundColor DarkCyan
    $lista = Processar-Arquivos -Descricao $cat.Descricao -CaminhoPasta $cat.Pasta -Padroes $cat.Padroes -MaisVelhoQueDias $cat.RetDias
    $MAPA_CATEGORIA_ARQUIVOS[$cat.Descricao] = $lista
    $soma = [long]0
    foreach ($f in $lista) { $soma += $f.Length }
    $cor = if ($lista.Count -eq 0) { "Gray" } else { "Yellow" }
    Write-Host ("   -> {0} arquivos marcados | Tamanho: {1}" -f $lista.Count, (FormatarTamanho $soma)) -ForegroundColor $cor
    if ($lista.Count -gt 0 -and $lista.Count -le 50) {
        foreach ($f in $lista | Sort-Object LastWriteTime -Descending) {
            $nm = $f.FullName.Replace($ROOT, ".")
            $t  = FormatarTamanho $f.Length
            $dt = $f.LastWriteTime.ToString("dd/MM/yyyy HH:mm")
            Write-Host ("      * {0,-70} {1,12}  {2}" -f $nm,$t,$dt) -ForegroundColor Gray
        }
    } elseif ($lista.Count -gt 50) {
        Write-Host ("      ... (mais {0} arquivos - suprimidos)" -f ($lista.Count - 50)) -ForegroundColor DarkGray
    }
    Write-Host
    $TOTAL_QTD += $lista.Count
    $TOTAL_TAMANHO += $soma
}

# ---------- Pastas vazias remover se vazias ------------------------
$PASTAS_PARA_REMOVER_SE_VAZIAS = New-Object System.Collections.ArrayList
if ($Force) {
    $candidatasVazias = @(
        $SCREENSHOTS_DIR,
        $AUDIT_EXPORTS,
        (Join-Path $AUDIT_DIR "__pycache__")
    )
    foreach ($pasta in $candidatasVazias) {
        if (-not (Test-Path -LiteralPath $pasta)) { continue }
        try {
            $conteudo = Get-ChildItem -LiteralPath $pasta -Force -ErrorAction SilentlyContinue
            if (-not $conteudo -or $conteudo.Count -eq 0) {
                $chk = Join-Path $pasta ".gitkeep"
                if (-not (Testa-ArquivoProtegido $chk)) { [void]$PASTAS_PARA_REMOVER_SE_VAZIAS.Add($pasta) }
            }
        } catch {}
    }
}

# ---------- RESUMO ANTES DE CONFIRMAR -----------------------------
Write-Host $SEP -ForegroundColor DarkYellow
Write-Host (" {0,82}" -f "[RESUMO ANTES DA EXECUCAO]" ) -ForegroundColor Yellow
Write-Host $SEP -ForegroundColor DarkYellow
Write-Host ("  Quantidade total de arquivos marcados:  {0}" -f $TOTAL_QTD) -ForegroundColor Yellow
Write-Host ("  Tamanho total a liberar:              {0}" -f (FormatarTamanho $TOTAL_TAMANHO)) -ForegroundColor Yellow
Write-Host ("  Subpastas vazias p/ remover (Force):  {0}" -f $PASTAS_PARA_REMOVER_SE_VAZIAS.Count) -ForegroundColor Yellow
Write-Host $SEP -ForegroundColor DarkYellow
Write-Host

# ---------- CONFIRMACAO ---------------------------------------
$RESP = "S"
if ($Force) {
    if ($TOTAL_QTD -eq 0 -and $PASTAS_PARA_REMOVER_SE_VAZIAS.Count -eq 0) {
        $RESP = "N"
        Write-Host "[INFO] Nenhum arquivo ou pasta para limpar." -ForegroundColor Green
    } elseif ($PSBoundParameters.ContainsKey('Confirm') -and -not $PSBoundParameters.Confirm) {
        $RESP = "S"
    } else {
        $respLida = Read-Host " CONFIRMA apagar os $TOTAL_QTD arquivos ACIMA? (S/N)  [Padrao = N]"
        if ([string]::IsNullOrWhiteSpace($respLida)) { $respLida = "N" }
        $RESP = $respLida.ToUpperInvariant()
    }
} else {
    Write-Host "[INFO] Modo DRY-RUN (use -Force p/ apagar de verdade). NENHUM arquivo foi apagado." -ForegroundColor Green
    exit 0
}

# ---------- EXECUCAO REAL APAGAR ------------------------------
if ($Force -and ($RESP -eq "S" -or $RESP -eq "SIM")) {
    $qtd_apagados = 0
    $tam_apagado = [long]0
    Write-Host
    Write-Host " Iniciando remocao dos arquivos..." -ForegroundColor Red
    foreach ($cat in $CATEGORIAS) {
        $lista = $MAPA_CATEGORIA_ARQUIVOS[$cat.Descricao]
        if ($lista.Count -eq 0) { continue }
        foreach ($f in $lista) {
            try {
                if (Testa-ArquivoProtegido $f.FullName) {
                    Write-Host ("    [PROTEGIDO - 2a checagem] Ignorando {0}" -f $f.Name) -ForegroundColor Magenta
                    continue
                }
                Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
                $qtd_apagados++
                $tam_apagado += $f.Length
            } catch {
                Write-Host ("    [ERRO] {0}  -> {1}" -f $f.Name, $_.Exception.Message) -ForegroundColor Red
            }
        }
    }
    $pastasRemovidas = 0
    foreach ($p in $PASTAS_PARA_REMOVER_SE_VAZIAS) {
        try {
            if (Test-Path -LiteralPath $p) {
                Remove-Item -LiteralPath $p -Force -Recurse -ErrorAction Stop
                $pastasRemovidas++
            }
        } catch {}
    }
    Write-Host
    Write-Host $SEP -ForegroundColor Green
    Write-Host (" {0,82}" -f "[CLEANUP CONCLUIDO]") -ForegroundColor Green
    Write-Host $SEP -ForegroundColor Green
    Write-Host ("   Arquivos removidos:       {0}" -f $qtd_apagados) -ForegroundColor Green
    Write-Host ("   Espaco liberado:          {0}" -f (FormatarTamanho $tam_apagado)) -ForegroundColor Green
    Write-Host ("   Pastas vazias limpas:    {0}" -f $pastasRemovidas) -ForegroundColor Green
    Write-Host ("   Retencao LGPD:          {0} dias" -f $RetencaoDias) -ForegroundColor Green
    Write-Host $SEP -ForegroundColor Green
} else {
    Write-Host " [CANCELADO] Operacao cancelada. Nada foi apagado." -ForegroundColor DarkYellow
}
Write-Host
exit 0
